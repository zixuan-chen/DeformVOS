class DefaultModelConfig():
    def __init__(self):
        self.MODEL_NAME = 'AOTDefault'

        self.MODEL_VOS = 'aot'
        self.MODEL_ENGINE = 'aotengine'
        self.MODEL_ALIGN_CORNERS = True
        self.MODEL_ENCODER = 'mobilenetv2'
        self.MODEL_ENCODER_PRETRAIN = './pretrain_models/mobilenet_v2-b0353104.pth'  # https://download.pytorch.org/models/mobilenet_v2-b0353104.pth
        self.MODEL_ENCODER_DIM = [24, 32, 96, 1280]  # 4x, 8x, 16x, 16x
        self.MODEL_ENCODER_EMBEDDING_DIM = 256
        self.MODEL_DECODER_INTERMEDIATE_LSTT = True
        self.MODEL_LINEAR_Q = True
        self.MODEL_NORM_INP = True
        self.MODEL_FREEZE_BN = True
        self.MODEL_FREEZE_BACKBONE = False
        self.MODEL_MAX_OBJ_NUM = 3 # 模型中最多的物体个数
        self.MODEL_IGNORE_TOKEN = True
        self.MODEL_SELF_HEADS = 8
        self.MODEL_ATT_HEADS = 8
        self.MODEL_LSTT_NUM = 1
        self.MODEL_EPSILON = 1e-5

        self.TRAIN_LONG_TERM_MEM_GAP = 9999

        self.TEST_LONG_TERM_MEM_GAP = 9999
