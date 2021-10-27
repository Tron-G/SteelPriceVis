# -*- coding:utf-8 -*-
import numpy

from keras.layers import Dense
from keras.layers import LSTM
from keras.models import Sequential, load_model
from sklearn.preprocessing import MinMaxScaler

class PricePredict:

    def create_dataset(self, dataset, look_back):
        # 这里的look_back与timestep相同
        dataX, dataY = [], []
        for i in range(len(dataset) - look_back - 1):
            # print(i, "--", i + look_back)
            a = dataset[i:(i + look_back)]
            # print(a)
            dataX.append(a)
            dataY.append(dataset[i + look_back])
        return numpy.array(dataX), numpy.array(dataY)

    def predictPrice(self, data):
        """
        输入时序数据进行训练和预测
        :param data: 一维时序数据
        :return:
        """
        # dataframe = pd.read_csv('files/'+steel_type+'.csv', usecols=[1], engine='python')
        data = data.values
        data = numpy.reshape(data, (len(data), 1))

        dataset = data
        # dataframe = data
        # dataset = dataframe.values
        dataset = dataset.astype("float32")
        # 归一化
        scaler = MinMaxScaler(feature_range=(0, 1))
        dataset = scaler.fit_transform(dataset)
        # 划分训练数据与测试数据
        train_size = int(len(dataset) * 0.65)
        trainlist = dataset[:train_size]
        # testlist = dataset[train_size:]

        # 构造数据
        look_back = 5
        trainX, trainY = self.create_dataset(trainlist, look_back)
        # testX, testY = create_dataset(testlist, look_back)
        trainX = numpy.reshape(trainX, (trainX.shape[0], trainX.shape[1], 1))
        # testX = numpy.reshape(testX, (testX.shape[0], testX.shape[1], 1))
        # 模型训练
        model = Sequential()
        model.add(LSTM(4, input_shape=(None, 1)))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')
        # verbose 0:为不在标准输出流输出日志信息 1:显示进度条 2:每个epoch输出一行记录
        model.fit(trainX, trainY, epochs=40, batch_size=1, verbose=1)
        # model.save(os.path.join("DATA", "Test" + ".h5"))
        # model = load_model(os.path.join("DATA","Test" + ".h5"))
        # 使用最后5个值预测下一天的
        input_data = dataset[-5:]
        input_data = numpy.reshape(input_data, (1, 5, 1))
        res = model.predict(input_data)
        # 反归一化
        res = scaler.inverse_transform(res)
        return res[0][0]
