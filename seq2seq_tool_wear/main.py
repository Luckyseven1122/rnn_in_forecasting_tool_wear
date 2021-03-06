from seq2seq_tool_wear.model import *
from data import RNNSeriesDataSet
from keras.callbacks import TensorBoard,ModelCheckpoint
import os.path
from keras.models import load_model
import matplotlib.pyplot as plt

# ---- need func --
def get_loss_value(real,pred):
    from sklearn.metrics import mean_squared_error,mean_absolute_error
    cnt = 0
    for i in pred:
        if i == None:
            cnt += 1
        else:
            break
    length = min(len(pred),len(real))
    return mean_squared_error(real[cnt:length],pred[cnt:length]),mean_absolute_error(real[cnt:length],pred[cnt:length])

# ---- CONF ------
LOG_DIR = "MAX_KERAS_ROI_LOG/"
PREDICT = True

# ---- GEN Data ----
data = RNNSeriesDataSet(10,20)
x,y = data.get_rnn_data()

# ---- shuffle -----
import random
# set random seeds so that we can get the same random data!
SEED = 12347
random.seed(SEED)
index = [i for i in range(len(y))]
random.shuffle(index)
train_y = y[index]
train_x = x[index]

print("Size :",train_x.shape,train_y.shape)

for DEPTH in [5]:

    HIDDEN_DIM = 128
    TRAIN_NAME = "Simple_2_5_Separate_RNN_Depth_%s_hidden_dim_%s" % (DEPTH,HIDDEN_DIM)
    MODEL_NAME = "%s.kerasmodel" % (TRAIN_NAME)
    MODEL_WEIGHT_NAME = "%s.kerasweight" % (TRAIN_NAME)
    MODEL_CHECK_PT = "%s.kerascheckpts" % (TRAIN_NAME)

    # model = build_model(1, 2, HIDDEN_DIM, 3, 1, DEPTH)
    model = build_simple_RNN((2,1),5,1)
    print(model.summary())
    print("Model has been built.")

    if not PREDICT:
        print("In [TRAIN] mode")
        # CALLBACK
        tb_cb = TensorBoard(log_dir=LOG_DIR + TRAIN_NAME)
        ckp_cb = ModelCheckpoint(MODEL_CHECK_PT, monitor='val_loss', save_weights_only=True, verbose=1,
                                 save_best_only=True, period=5)

        if os.path.exists(MODEL_CHECK_PT):
            model.load_weights(MODEL_CHECK_PT)
            print("load checkpoint successfully")
        else:
            print("No checkpoints found !")
        print("Start to train the model")

        model.fit(train_x,train_y,batch_size=16,epochs=5000,validation_split=0.2,callbacks=[tb_cb,ckp_cb])

        model.model.save(MODEL_NAME)
        model.save_weights(MODEL_WEIGHT_NAME)

    else:
        if os.path.exists(MODEL_CHECK_PT):
            model.load_weights(MODEL_CHECK_PT)
            print("load checkpoint successfully")
        else:
            print("No checkpoints found! try to load model directly")
            model = load_model(MODEL_NAME)

        tool_wear_data = data.max_tool_wear_data

        for knife_number in range(3):
            if knife_number < 2 :
                continue
            knife_data = tool_wear_data[knife_number*315:(knife_number+1)*315]
            print("Current Knife shape:",knife_data.shape)
            first_list = [None,None,]
            second_list = [None,None,None]
            third_list = [None,None,None,None]
            fourth_list = [None for _ in range(5)]
            fifth_list = [None for _ in range(6)]
            fig = plt.figure(0)
            for every_start in range(knife_data.shape[0]-5):
                predicted = model.predict(knife_data[every_start:every_start+2].reshape(1,2,1)).reshape(5)

                first_list.append(predicted[0])
                second_list.append(predicted[1])
                third_list.append(predicted[2])
                fourth_list.append(predicted[3])
                fifth_list.append(predicted[4])


            plt.plot(knife_data,label="REAL")
            plt.scatter([i for i in range(len(first_list))],first_list,label="1st forecast value",s=2,marker="x")
            plt.scatter([i for i in range(len(second_list))],second_list, label="2nd forecast value",s=2,marker="o")
            plt.scatter([i for i in range(len(third_list))],third_list, label="3rd forecast value",s=2,marker="v")
            plt.scatter([i for i in range(len(fourth_list))],fourth_list, label="4th forecast value",s=2,marker=",")
            plt.scatter([i for i in range(len(fifth_list))],fifth_list, label="5th forecast value",s=2,marker=".")
            print("Pred ",len(first_list),len(second_list),len(third_list),len(fourth_list),len(fifth_list))
            # calculate MSE
            print(get_loss_value(knife_data,first_list))
            print(get_loss_value(knife_data, second_list))
            print(get_loss_value(knife_data, third_list))
            print(get_loss_value(knife_data, fourth_list))
            print(get_loss_value(knife_data, fifth_list))

            plt.xlabel("Run")
            plt.ylabel("Tool wear ($\mu m$)")

            plt.legend()
            plt.savefig("../res/short_c%s.pdf"%(knife_number+1))
            plt.show()
            plt.close(0)






