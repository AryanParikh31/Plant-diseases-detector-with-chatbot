from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNet
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import json

# Define image size and batch size
img_size = (224, 224)
batch_size = 32

# Data generators
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    'dataset', target_size=img_size, batch_size=batch_size,
    class_mode='categorical', subset='training'
)

val_generator = train_datagen.flow_from_directory(
    'dataset', target_size=img_size, batch_size=batch_size,
    class_mode='categorical', subset='validation'
)

# Load MobileNet
base_model = MobileNet(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False  # Freeze base model

# Add custom layers
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(train_generator.num_classes, activation='softmax')(x)

# Create the model
model = Model(inputs=base_model.input, outputs=predictions)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(train_generator, validation_data=val_generator, epochs=10)

# Save model
model.save('plant_disease_model.h5')

# Save class names
class_names = list(train_generator.class_indices.keys())
with open('class_names.json', 'w') as f:
    json.dump(class_names, f)

print("Model training complete and saved!")
