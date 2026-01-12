# GIS (Geographic Information System) Imagery Auto-labeler for Object Detection Model Training 

We were training an Object Detection model to detect power substations in satellite imagery. In order to train the model we needed thousands of labeled images with correctly set borders. 

I set out to create an program using traditional computer vision means that would be able to generate a training data set of over 10k images that could be used to train the model. Otherwise the images would all have to be manually labeled. 

So this does have some circular logic to it - after all if we can train a computer vision model to label the images why bother with the Object Detection Model. To answer that question: we were able to provide the auto-labeler with some major advantages that the model would not have: We used gps coordinates of known power substations to pull GIS images with the substations roughly centered in those images. Knowing the Substation was roughly centered in the image was foundational to the CV algorithm. 


The methodologies and algorithm I used to box the substations in the image are described below, as well as some example labeled data. 



![auto-labeler description](./assets/auto-labeler%20description.png)