from fastapi import FastAPI
import cv2
import uvicorn
import os

app = FastAPI()  # 创建 api 对象


@app.get("/")  # 根路由
async def root():
    return {"武汉": "加油！！！"}


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

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=6788,
                log_level="info", reload=True)
