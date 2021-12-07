from fastapi import FastAPI, HTTPException
import cv2
import uvicorn
import os

from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from pydantic import BaseModel

# connect to mongodb
DB_CLIENT = AsyncIOMotorClient('127.0.0.1', 27017)
DB = DB_CLIENT['test']  # 库名称

app = FastAPI()  # 创建 api 对象


@app.get("/pic/{path}")
async def zipping(path: str, q: int = None):
    pic_name = os.path.basename(path)
    src_path = os.path.join('/www/wwwroot/shushuo.space/upload/pic/', pic_name)
    dir_path = os.path.join(
        '/www/wwwroot/shushuo.space/upload/zipped_pic/', pic_name)
    if ".gif" in pic_name:
        return {"path": src_path}
    if os.path.exists(dir_path):
        return {"path": dir_path}
    img = cv2.imread(src_path)

    heigh, width = img.shape[:2]

    if heigh+width/2 > 1000:
        compress_rate = 0.1
    elif heigh+width/2 > 500:
        compress_rate = 0.2
    elif heigh+width/2 > 250:
        compress_rate = 0.35
    else:
        compress_rate = 0.5
    img_resize = cv2.resize(img, (int(width*compress_rate), int(heigh*compress_rate)),
                            interpolation=cv2.INTER_AREA)  # 双三次插值

    zip_num = 10
    cv2.imwrite(dir_path, img_resize, [cv2.IMWRITE_JPEG_QUALITY, zip_num])
    return {"path": dir_path}


class Item(BaseModel):
    # 数据模型
    name: str = None
    address: str = None
    age: int = None
    school: str = None
    dec: dict = None


def fix_item_id(item):
    """
    二次校验数据
    :param item:
    :return:
    """
    if item.get("_id", False):
        item["_id"] = str(item["_id"])
        return item
    else:
        raise ValueError(
            f"No `_id` found! Unable to fix item ID for item: {item}")


@app.get("/items/{id_}", tags=["items"])
async def read_item(id_: str):
    """
    根据条件搜索数据
    """
    # item_name =
    the_item = await DB.users_copy1.find_one({"_id": ObjectId(id_)})  # item为集合名称
    if the_item:
        return fix_item_id(the_item)
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/items/", tags=["items"])
async def get_all_items(limit: int = 0):  # 可以指定跳过值
    """
    获取所有的数据记录
    :param limit:
    :param skip:
    :return:
    """
    # items_cursor = DB.item.find().skip(skip).limit(limit)
    # items = await items_cursor.to_list(length=limit)
    if limit > 0:
        n = limit
    else:
        n = await DB.item.count_documents({})
    items_cursor = DB.item.find()
    items = await items_cursor.to_list(n)
    return list(map(fix_item_id, items))


@app.post("/items/", tags=["items"])
async def create_item(item: Item):
    """
    新增数据
    :param item:
    :return:
    """
    result = await DB.item.insert_one(item.dict())
    the_item = await DB.item.find_one({"_id": result.inserted_id})
    return fix_item_id(the_item)


@app.delete("/items/{id_}", tags=["items"])
async def delete_item(id_: str):
    """
    删除数据
    :param id_: object_id  运用中可以修改该条件
    :return:
    """
    item_op = await DB.item.delete_one({"_id": ObjectId(id_)})
    if item_op.deleted_count:
        return {"status": f"deleted count: {item_op.deleted_count}"}


@app.put("/items/{_id}", tags=["items"])
async def update_item(_id: str, item_data: Item):
    """
    更新单条mongodb数据
    :param _id: 该条数据对应的object_id
    :param item_data: json格式
    :return:
    """
    id_ = ObjectId(_id)
    item_op = await DB.item.update_one(
        {"_id": id_}, {"$set": item_data.dict()}
    )
    if item_op.modified_count:
        item = await DB.item.find_one({"_id": id_})
        return fix_item_id(item)
    else:
        raise HTTPException(status_code=304)


@app.on_event("startup")
async def app_startup():
    print('\nApi running...\n')


@app.on_event("shutdown")
async def app_shutdown():
    # close connection to DB
    DB_CLIENT.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=6788,
                log_level="info", reload=True)
