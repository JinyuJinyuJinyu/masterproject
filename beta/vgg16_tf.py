import tensorflow as tf
import utils
import numpy as np
import json
import time
from tensorflow.keras.preprocessing.image import ImageDataGenerator

tf.random.set_seed(0)

class Block1(tf.keras.layers.Layer):
    def __init__(self,filters,kernel_size=(3,3), stride=1):
        super(Block1, self).__init__()
        self.con2a = tf.keras.layers.Conv2D(filters,kernel_size,strides=stride,padding='same',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        self.bn2a = tf.keras.layers.BatchNormalization()
        self.relua = tf.keras.layers.Activation('relu')
        self.dropouta = tf.keras.layers.Dropout(0.4)


        self.con2b = tf.keras.layers.Conv2D(filters,kernel_size,strides=stride,padding='same',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        self.bn2b = tf.keras.layers.BatchNormalization()
        self.relub = tf.keras.layers.Activation('relu')

        self.pool = tf.keras.layers.MaxPool2D(pool_size=(2,2),strides=(2,2),padding='same')
    def call(self, input_tensor, training=None):
        x = self.con2a(input_tensor)
        x = self.bn2a(x,training=training)
        x = self.relua(x)
        x = self.dropouta(x)

        x = self.con2b(x)
        x = self.bn2b(x,training=training)
        x = self.relub(x)

        x = self.pool(x)
        return x

class Block2(tf.keras.layers.Layer):
    def __init__(self,filters,kernel_size=(3,3), stride=1):
        super(Block2,self).__init__()
        self.con2a = tf.keras.layers.Conv2D(filters,kernel_size,strides=stride,padding='same',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        self.bn2a = tf.keras.layers.BatchNormalization()
        self.relua = tf.keras.layers.Activation('relu')
        self.dropouta = tf.keras.layers.Dropout(0.5)

        self.con2b = tf.keras.layers.Conv2D(filters,kernel_size,strides=stride,padding='same',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        self.bn2b = tf.keras.layers.BatchNormalization()
        self.relub = tf.keras.layers.Activation('relu')
        self.dropoutb = tf.keras.layers.Dropout(0.5)

        self.con2c = tf.keras.layers.Conv2D(filters,kernel_size,strides=stride,padding='same',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        self.bn2c = tf.keras.layers.BatchNormalization()
        self.reluc = tf.keras.layers.Activation('relu')

        self.pool = tf.keras.layers.MaxPool2D(pool_size=(2,2),strides=(2,2),padding='same')
    def call(self, input_tensor, training=None):
        x = self.con2a(input_tensor)
        x = self.bn2a(x,training=training)
        x = self.relua(x)
        x = self.dropouta(x)

        x = self.con2b(x)
        x = self.bn2b(x,training=training)
        x = self.relub(x)
        x = self.dropoutb(x)

        x = self.con2c(x)
        x = self.bn2c(x,training=training)
        x = self.reluc(x)

        x = self.pool(x)
        return x

class vgg16(tf.keras.models.Model):

    def __init__(self,num_classes):
        super(vgg16,self).__init__()

        self.block2xa = self._make_layers(Block1, [64,128],stride=1)

        self.block3xb = self._make_layers(Block2, [256,512,512], stride=1)

        self.flattena = tf.keras.layers.Flatten(name='flatten')
        self.densea = tf.keras.layers.Dense(512,activation='relu',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))
        #4096
        self.denseb = tf.keras.layers.Dense(4096,activation='relu',
                                            kernel_regularizer=tf.keras.regularizers.l2(5e-4))

        self.densec = tf.keras.layers.Dense(units=num_classes,activation='softmax')
    # build block layers
    def _make_layers(self,block,filters,stride=1):
        convlayers = tf.keras.Sequential()

        for flter in filters:
            convlayers.add(block(flter,stride))

        return convlayers
    def call(self,inputs, training=None):

        x = self.block2xa(inputs,training=training)
        x = self.block3xb(x,training=training)

        x = self.flattena(x)
        x = self.densea(x)
        # x = self.denseb(x)
        x = self.densec(x)

        return x



def preprocess(x_batch,y_batch):
    x_batch = tf.cast(x_batch, dtype=tf.float32) /255. - 0.5
    y_batch = tf.cast(y_batch, dtype=tf.int32)
    return x_batch, y_batch



# batch_size = 32
epochs = 20

number_samples=10000
batch_size = 64

(x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()

# x_train = x_train.astype('float32')
# x_test = x_test.astype('float32')
#
#
# y_train = tf.keras.utils.to_categorical(y_train, 10)
# y_test = tf.keras.utils.to_categorical(y_test, 10)

y_train = tf.squeeze(y_train,axis=1)

# _,x_val,_,y_val = train_test_split(x_test,y_test,test_size=0.2,shuffle=True)
# y_val = tf.squeeze(y_val, axis=1)


train_set = tf.data.Dataset.from_tensor_slices((x_train,y_train))
train_set = train_set.shuffle(1024).map(preprocess).batch(batch_size)

val_set = tf.data.Dataset.from_tensor_slices((x_test,y_test))
val_set = val_set.map(preprocess).batch(batch_size)




# x_train, x_test, y_train, y_test = utils.load_dat()
#
# number_samples = y_test.shape[0]

# print(x_train.dtype,x_test.dtype,y_train.dtype,y_test.dtype)
# print(y_train.shape)


# global_step = tf.Variable(0, trainable=False)
# starter_learning_rate = 1e-3
# learning_rate = tf.compat.v1.train.exponential_decay(starter_learning_rate, global_step,100000, 0.96, staircase=True)
#
# train_set = tf.data.Dataset.from_tensor_slices((x_train,y_train))
# train_set = train_set.map(preprocess).batch(batch_size)
#
#
# val_set = tf.data.Dataset.from_tensor_slices((x_test,y_test))
# val_set = val_set.map(preprocess).batch(batch_size)

# optis = [tf.keras.optimizers.SGD(learning_rate,momentum=0.9).minimize(loss,global_step=global_step)]
optis = [tf.keras.optimizers.SGD(0.1,decay=1e-6,momentum=0.9, nesterov=True)]
f_name = ['SGD_VGG16_tf.json']



def main(optimizer,fname):

    VGG16 = vgg16(10)
    # make sure input shape equal to image size input shape = (None,image_size,image_size,3)
    VGG16.build(input_shape=(None,32,32,3))
    # learning_rate = 0.1
    # lr_drop = 20
    # sgd = tf.keras.optimizers.SGD(learning_rate,decay=1e-6,momentum=0.9, nesterov=True)
    # VGG16.compile(loss='categorical_crossentropy', optimizer=sgd,metrics=['accuracy'])
    #
    # def lr_scheduler(epoch):
    #     return learning_rate * (0.5 ** (epoch // lr_drop))
    #
    # reduce_lr = tf.keras.callbacks.LearningRateScheduler(lr_scheduler)
    #
    # VGG16.fit(x=x_train,y=y_train,batch_size=64,epochs=200,validation_data=(x_test,y_test),callbacks=[reduce_lr])
    # exit()
    f = open(fname, "w", encoding='utf-8')
    outfile = []

    @tf.function
    def train_step(x_batch, y_batch):
        with tf.GradientTape() as tape:
            logits = VGG16(x_batch, training=True)
            y_onehot = tf.one_hot(y_batch, depth=10)
            loss_value = tf.keras.losses.categorical_crossentropy(y_onehot, logits, from_logits=True)
        grads = tape.gradient(loss_value, VGG16.trainable_variables)
        optimizer.apply_gradients(zip(grads, VGG16.trainable_variables))
        return loss_value


    def val_step(x_batch_val, y_batch_val):

        val_logits = VGG16(x_batch_val, training=False)
        y_onehot_val = tf.one_hot(y_batch_val, depth=10)
        loss = tf.keras.losses.categorical_crossentropy(y_onehot_val, val_logits, from_logits=True)
        loss = tf.reduce_sum(loss)

        prob = tf.nn.softmax(val_logits,axis=1)
        preds = tf.argmax(prob, axis=1)
        preds = tf.cast(preds, dtype=tf.int32)
        mtx = tf.math.confusion_matrix(y_batch_val, preds, num_classes=10)


        return loss, mtx

    val_time = 0
    print('start training TensorFlow')
    start_time = init_time = time.time()
    for epoch in range(1, epochs + 1):
        # train
        for step, (x_batch, y_batch) in enumerate(train_set):
            train_step(x_batch, y_batch)

        if True:
            print('validating epoch: ',epoch)
            val_start_time = time.time()
            val_info = {}
            # print('validating')
            lossess = 0
            confusion_matrix = np.zeros((10, 10))

            for x_batch_val, y_batch_val in val_set:
                loss, confusion_mtx = val_step(x_batch_val, y_batch_val)

                confusion_matrix = np.add(confusion_matrix, confusion_mtx)
                lossess += loss.numpy()

            val_info['epoch: '] = epoch
            val_info['loss'] = lossess / number_samples
            val_info['accu'] = (tf.linalg.trace(confusion_matrix).numpy() / number_samples) * 100
            if epoch % epochs == 0:
                val_info['confusion matrix'] = confusion_matrix.tolist()
            print('accu: ',
                  (tf.linalg.trace(confusion_matrix).numpy() / number_samples) * 100)
            outfile.append(val_info)
            val_time += (time.time() - val_start_time)
        if epoch == 1:
            init_time = time.time() - init_time

    ttl_time = {}
    ttl_time['training time'] = (time.time() - start_time - val_time)
    ttl_time['total time'] = (time.time() - start_time)
    ttl_time['val time'] = val_time
    ttl_time['init time'] = init_time
    outfile.append(ttl_time)
    json.dump(outfile, f, separators=(',', ':'), indent=4)
    f.close()

if __name__ == '__main__':
    for opti,f in zip(optis,f_name):
        main(opti, f)
