# Parallel Image Processing using Multi-Threading

## Overview
This project demonstrates the concept of **parallelism using multi-threading** to process a large number of images efficiently.

Instead of processing images sequentially, the application distributes image processing tasks across multiple threads, allowing several images to be processed at the same time.

The goal of this project is to show how multi-threading can improve performance when working with **large datasets such as image collections**.

---

## Project Objective
- Demonstrate **parallel processing using multi-threading**
- Handle **multiple image files efficiently**
- Reduce processing time compared to sequential execution
- Provide a simple example of applying parallelism in real applications

---

## How It Works
1. The program reads all images from an input directory.
2. The list of images is divided into smaller tasks.
3. A **thread pool** is created.
4. Each thread processes one image at a time.
5. The processed images are saved to an output directory.

This allows multiple images to be processed simultaneously.

---

## Image Processing Task
To keep the project simple, each image undergoes a basic transformation such as:

- Resizing the image  
or  
- Converting the image format (e.g., PNG → JPG)

---

## Parallel Processing Architecture

Input Images  
↓  
Task Distribution  
↓  
Thread Pool (Multi-Threading)  
↓  
Parallel Image Processing  
↓  
Output Images

---

## Technologies Used
- **Java**
- **Java Multi-Threading**
- **ExecutorService (Thread Pool)**
- Standard Java image libraries

---

## Why Multi-Threading
Processing images one by one can be slow when the dataset is large.

By using multi-threading:
- Multiple images are processed **in parallel**
- CPU resources are used more efficiently
- Total execution time is reduced

---

## Example Workflow
1. Place images in the `input_images` folder  
2. Run the application  
3. The program processes images using multiple threads  
4. Processed images appear in the `output_images` folder  

---

## Future Improvements (Optional)
- Support more image filters
- Allow dynamic thread configuration
- Add performance comparison between sequential and parallel processing

---

## Conclusion
This project demonstrates a simple and practical use of **parallel programming with multi-threading**.  
It shows how large collections of files such as images can be processed faster by distributing tasks across multiple threads.
