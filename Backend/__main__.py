import os

from models.qcsi.mask import mask
from app import app
from flask_cors import CORS


def init_models():
    names = []
    model_path = r"./models"
    for model_path_dir in os.listdir(model_path):
        # 阻絕 "__pycache__" folder
        if model_path_dir.startswith("_"):
            continue

        # 判斷該資料夾是否為 *符合條件* 的model
        """
            符合條件：
            欲新增的model都應該需要符合以下條件：
            1. folder名稱就是model的名稱
            2. 裡面有predict() function，負責做該model的predict，input attribute為patient_data_dict <type: dictionary>
            3. 該model會預設從model.py中去抓取predict function (方法： 預設是＿＿init__.py裡面會寫"from .model import predict")
               如果predict function不在model.py中，則需要修改__init__.py中的路徑
        """
        if os.path.isdir("{}/{}".format(model_path, model_path_dir)) and \
                os.path.exists("{}/{}/model.py".format(model_path, model_path_dir)):
            names.append(model_path_dir)

    models_init_file = open("./models/__init__.py", "w")
    models_init_file.write("__all__ = {}\n".format(names))
    models_init_file.close()


if __name__ == '__main__':
    mask()
    init_models()
    CORS(app)
    app.debug = True
    app.run()
