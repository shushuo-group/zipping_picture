from fastapi import FastAPI, HTTPException, File, Form, UploadFile
import cv2
import uvicorn
import os
import time

from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId  # mongo存储的数据在没有特别指定_id数据类型时，默认类型为ObjectID
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

# nozip_dir 未压缩图片文件夹路径
nozip_dir = '/www/wwwroot/shushuo.space/upload/pic/'
debug_nozip_dir = '必须为网站目录下对应的文件夹目录'

# 调试的时候把下面一行解开注释即可
# nozip_dir = debug_nozip_dir

# zip_dir 已压缩图片文件夹路径
zip_dir = '/www/wwwroot/shushuo.space/upload/zipped_pic/'
debug_zip_dir = '必须为网站目录下对应的文件夹目录'

# 调试的时候把下面一行解开注释即可
# zip_dir = debug_zip_dir

# connect to mongodb
DB_CLIENT = AsyncIOMotorClient('127.0.0.1', 27017)
DB = DB_CLIENT['shushuo']  # 库名称

app = FastAPI()  # 创建 api 对象

# 调试所需origin
debug_origin = "http://localhost:8080"

origins = [
    debug_origin,
    "https://www.shushuo.space",
    "https://shushuo.space"
]


# 解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/pic/{path}")
async def zipping(path: str):
    # pic_name  like  abc.png
    pic_name = os.path.basename(path)
    # src_path -> nozip
    src_path = os.path.join(nozip_dir, pic_name)
    # dir_path -> zip
    dir_path = os.path.join(zip_dir, pic_name)

    if os.path.exists(dir_path):  # 已经存在压缩就不再执行后续
        return {"path": pic_name}

    elif pic_name.lower().endswith(".gif"):  # 不压缩gif
        return HTTPException(
            status_code=404, detail=f"No zipping gif image: {pic_name}!"
        )

    img = cv2.imread(src_path)
    if img is None:
        return HTTPException(
            status_code=404, detail=f"No img: {pic_name} found!"
        )
    heigh, width = img.shape[:2]

    if os.path.getsize(src_path) < 100 * 1024:  # 文件大小小于100KB
        compress_rate = 0.75
    elif (heigh+width)/2 > 4000:
        compress_rate = 0.15
    elif (heigh+width)/2 > 2000:
        compress_rate = 0.3
    elif (heigh+width)/2 > 1000:
        compress_rate = 0.35
    elif (heigh+width)/2 > 500:
        compress_rate = 0.4
    elif (heigh+width)/2 > 250:
        compress_rate = 0.45
    else:
        compress_rate = 0.5

    img_resize = cv2.resize(
        img, (int(width * compress_rate), int(heigh * compress_rate)),
        interpolation=cv2.INTER_AREA)  # 改变图片大小，使用双三次插值

    zip_num = min(65, max(35, int(compress_rate * 100)))
    cv2.imwrite(dir_path, img_resize, [
                cv2.IMWRITE_JPEG_QUALITY, zip_num])  # 质量降低
    return {"path": pic_name}


class Item(BaseModel):
    # 数据模型
    name: str = None
    email: str = None
    id_: str = None
    account: str = None


def fix_item_id(item):
    """
    二次校验数据
    :param item:检验的条目
    :return:本身条目
    """
    if item.get("_id", False):
        item["_id"] = str(item["_id"])
        return item
    else:
        raise HTTPException(
            status_code=404, detail=f"No `_id` found! Unable to fix item ID for item: {item}")


@app.get("/items/{token}", tags=["items"])
async def read_token(token: str):
    """
    根据条件搜索数据，返回用户账号id
    """
    # item_name =
    # item为集合名称
    the_item = await DB.users.find_one({"token": token})
    if the_item and the_item['token'] == token:
        return fix_item_id(the_item)['userAccount']
    else:
        raise HTTPException(status_code=404, detail="Token not found")


# @app.get("/items/", tags=["items"])
# async def get_all_items(limit: int = 0):
#     """
#     获取所有的数据记录
#     :param limit:
#     :param skip:
#     :return:
#     """
#     # items_cursor = DB.item.find().skip(skip).limit(limit)
#     # items = await items_cursor.to_list(length=limit)
#     if limit > 0:
#         n = limit
#     else:
#         n = await DB.item.count_documents({})
#     items_cursor = DB.item.find()
#     items = await items_cursor.to_list(n)
#     return list(map(fix_item_id, items))


# @app.post("/items/", tags=["items"])
# async def create_item(item: Item):
#     """
#     新增数据
#     :param item:
#     :return:
#     """
#     result = await DB.item.insert_one(item.dict())
#     the_item = await DB.item.find_one({"_id": result.inserted_id})
#     return fix_item_id(the_item)


# @app.delete("/items/{id_}", tags=["items"])
# async def delete_item(id_: str):
#     """
#     删除数据
#     :param id_: object_id  运用中可以修改该条件
#     :return:
#     """
#     item_op = await DB.item.delete_one({"_id": ObjectId(id_)})
#     if item_op.deleted_count:
#         return {"status": f"deleted count: {item_op.deleted_count}"}


# @app.put("/items/{_id}", tags=["items"])
# async def update_item(_id: str, item_data: Item):
#     """
#     更新单条mongodb数据
#     :param _id: 该条数据对应的object_id
#     :param item_data: json格式
#     :return:
#     """
#     id_ = ObjectId(_id)
#     item_op = await DB.item.update_one(
#         {"_id": id_}, {"$set": item_data.dict()}
#     )
#     if item_op.modified_count:
#         item = await DB.item.find_one({"_id": id_})
#         return fix_item_id(item)
#     else:
#         raise HTTPException(status_code=304)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...), token: str = Form(...)):
    # token识别
    user_id = await read_token(token)
    # 保存图片
    contents = await file.read()
    temp_time = round(time.time()*1000)
    file.filename = user_id+'_'+str(temp_time)+os.path.splitext(file.filename)[-1]
    src_path = os.path.join(
        nozip_dir, file.filename)

    # gif图片由前端完成压缩 即不需要压缩 直接进行存储
    if file.filename.lower().endswith(".gif"):
        dir_path = os.path.join(zip_dir, file.filename)
        with open(dir_path, 'wb') as f:  # gif直接保存在压缩后的文件夹
            f.write(contents)
        return {"path": file.filename}

    with open(src_path, 'wb') as f:  # 其余保存在原图文件夹
        f.write(contents)
    # 返回的是压缩后的路径
    return await zipping(file.filename)


@app.on_event("startup")
async def app_startup():
    print('\nApi running...\n')


@app.on_event("shutdown")
async def app_shutdown():
    # close connection to DB
    DB_CLIENT.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=6788,
                log_level="info", reload=True)
