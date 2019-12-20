import tensorflow as tf


def my_conv(filters, kernel_size=(3, 3), stride=1, activation='relu', name=''):
    def forward(x):
        x = tf.keras.layers.Conv2D(
            filters,
            kernel_size,
            strides=stride,
            padding='same',
            name=name + '_conv')(x)
        x = tf.keras.layers.BatchNormalization(name=name + '_batchnorm')(x)
        x = tf.keras.layers.Activation(activation, name=name + '_' + activation)(x)
        return x

    return forward


def my_deconv(filters, kernel_size=(3, 3), stride=1, activation='relu', name=''):
    def forward(x):
        x = tf.keras.layers.Conv2DTranspose(
            filters,
            kernel_size,
            strides=stride,
            padding='same',
            name=name + '_conv')(x)
        x = tf.keras.layers.BatchNormalization(name=name + '_batchnorm')(x)
        x = tf.keras.layers.Activation(activation, name=name + '_' + activation)(x)
        return x

    return forward


def res_block(filters, kernel_size=(3, 3), stride=1, first=False, name=''):
    def forward(x):
        x_shortcut = x

        # don't repeat bn->relu since we just did it
        if not first:
            x = tf.keras.layers.BatchNormalization(name=name + '_batchnorm1')(x)
            x = tf.keras.layers.Activation('relu', name=name + '_relu1')(x)
        x = tf.keras.layers.Conv2D(
            filters,
            kernel_size,
            strides=stride,
            padding='same',
            name=name + '_conv1')(x)

        x = tf.keras.layers.BatchNormalization(name=name + '_batchnorm2')(x)
        x = tf.keras.layers.Activation('relu', name=name + '_relu2')(x)
        x = tf.keras.layers.Conv2D(
            filters,
            kernel_size,
            padding='same',
            name=name + '_conv2')(x)

        x = tf.keras.layers.Add(name=name + '_shortcut')([x, x_shortcut])
        return x

    return forward


def normalize_img(x):
    return x / 255.0


def denormalize_img(x):
    return (x + 1) * 127.5


def build_model(input_shape, name='resnet'):
    with tf.variable_scope(name):
        x_input = tf.keras.layers.Input(input_shape, name='input')

        x = tf.keras.layers.Lambda(normalize_img, name='normalize')(x_input)
        x = my_conv(32, (9, 9), name='conv1')(x)
        x = my_conv(64, (3, 3), stride=2, name='conv2')(x)
        x = my_conv(128, (3, 3), stride=2, name='conv3')(x)

        x = res_block(128, (3, 3), stride=1, name='resblock1', first=True)(x)
        x = res_block(128, (3, 3), stride=1, name='resblock2')(x)
        x = res_block(128, (3, 3), stride=1, name='resblock3')(x)
        x = res_block(128, (3, 3), stride=1, name='resblock4')(x)
        x = res_block(128, (3, 3), stride=1, name='resblock5')(x)

        x = my_deconv(64, (3, 3), stride=2, name='deconv1')(x)
        x = my_deconv(32, (3, 3), stride=2, name='deconv2')(x)
        x = my_deconv(3, (9, 9), activation='tanh', name='deconv3')(x)
        x = tf.keras.layers.Lambda(denormalize_img, name='denormalize')(x)

        model = tf.keras.models.Model(inputs=x_input, outputs=x, name=name)
        return model
