import tensorflow as tf
import numpy as np

class BiddingPolicyNetwork:

    def __init__(self, name):

        self.numHiddenNeurons = 6
        self.numOutputNeurons = 5 # KARO, HERC, PIK, TREF, dalje

        self.trues = [True] * (self.numOutputNeurons - 1)

        with tf.variable_scope("BiddingPolicyNetwork_{}".format(name)):
            self.session=tf.Session()

            self.statePlaceholder = tf.placeholder(dtype=tf.float32, shape=(None, 32), name="statePlaceholder")
            self.mustMaskPlaceholder = tf.placeholder(dtype=tf.bool, shape=(None, self.numOutputNeurons), name="mustMaskPlaceholder")
            self.rewardPlaceholder = tf.placeholder(dtype=tf.float32, shape=(None,), name="rewardPlaceholder")
            self.actionPlaceholder = tf.placeholder(dtype=tf.int32, shape=(None,), name="actionPlaceholder")

            self.W1 = tf.get_variable(name="W1", shape=(32,self.numHiddenNeurons), initializer=tf.contrib.layers.xavier_initializer())
            self.b1 = tf.Variable(initial_value=tf.constant(0.0, shape=(self.numHiddenNeurons,), dtype=tf.float32), name="b1")
            z1 = tf.nn.xw_plus_b(self.statePlaceholder, self.W1, self.b1, name="z1")
            h1 = tf.nn.relu(z1)

            self.W2 = tf.get_variable(name="W2", shape=(self.numHiddenNeurons, self.numOutputNeurons), initializer=tf.contrib.layers.xavier_initializer())
            self.b2 = tf.Variable(initial_value=tf.constant(0.0, shape=(self.numOutputNeurons,), dtype=tf.float32), name="b2")
            z2 = tf.nn.xw_plus_b(h1, self.W2, self.b2, name="z2")

            zeros = tf.zeros_like(self.mustMaskPlaceholder, dtype=tf.float32)

            maskedOutput = tf.where(condition = self.mustMaskPlaceholder, x = tf.nn.softmax(z2), y = zeros)
            self.output = maskedOutput / tf.reduce_sum(maskedOutput)
            reshapedOutput = tf.reshape(self.output, shape=(-1,))

            outputShape = tf.shape(self.output)
            batchSize = outputShape[0]

            self.responsibleIndices = tf.range(0, batchSize)*self.numOutputNeurons + self.actionPlaceholder
            self.responsibleNeurons = tf.gather(reshapedOutput, indices=self.responsibleIndices)

            self.loss = -tf.reduce_mean(tf.log(self.responsibleNeurons + 1e-9) * self.rewardPlaceholder)

            optimizer = tf.train.AdamOptimizer()
            self.trainOp = optimizer.minimize(self.loss)

            self.index = tf.argmax(self.output, axis=1)

            self.session.run(tf.global_variables_initializer())

    def train(self, action, state, reward):
        mustMask = np.array([self.trues + [True]])
        loss, _ = self.session.run(
            [self.loss, self.trainOp],
            feed_dict={
                self.actionPlaceholder: action,
                self.statePlaceholder: state,
                self.mustMaskPlaceholder: mustMask,
                self.rewardPlaceholder: reward
            }
        )
        return loss

    def feed(self, state, must):
        mustMask = np.array([self.trues + [not must]])
        output, index = self.session.run([self.output, self.index], feed_dict={self.statePlaceholder: state, self.mustMaskPlaceholder: mustMask})
        print(output)
        return output[0], index[0]
