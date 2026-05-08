# Smart Bulk Image Processor

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-org/smart-bulk-image-processor/actions) [![Java](https://img.shields.io/badge/java-21-blue.svg)](https://www.oracle.com/java/) [![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**Smart Bulk Image Processor** is a modular, high‑performance Java application designed to apply transformations to large collections of images in a robust, repeatable fashion. It leverages **Spring Boot 3.2**, **Spring Batch**, and modern Java features to demonstrate best practices in batch processing and concurrent execution.

The codebase is intended for educational use, prototypes, or as a starting point for more sophisticated image‑processing pipelines.

---

## Table of contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Project structure](#project-structure)
4. [Getting started](#getting-started)
5. [Configuration](#configuration)
6. [Extending the project](#extending-the-project)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)

## Features

- **Read–Process–Write workflow** powered by Spring Batch.
- **Concurrent processing** through a configurable `ThreadPoolTaskExecutor`.
- Pluggable **image processing strategies** (grayscale, resize, etc.) that can be added as Spring components.
- Automatic job startup with embedded H2 database for metadata.
- Self‑healing directory creation for `images/input` and `images/output`.

## Architecture

The solution adheres to separation of concerns and micro‑service style modularity, grouping responsibilities by layer:

1. **Reader (`ImageJobReader`)** – enumerates files from the input directory and constructs `ImageJob` DTOs.
2. **Processor (`ImageJobProcessor`)** – applies a strategy to each job using `ImageProcessingService`.
3. **Writer (`ImageJobWriter`)** – writes the result image to the output directory, preserving file format.
4. **Configuration (`BatchConfig`)** – defines the Spring Batch `Job`/`Step` and configures thread pool parameters.
5. **Strategy plugins** – implement `ImageProcessingStrategy`; each strategy is a Spring bean, enabling zero‑touch extensibility.

By default, the batch step processes items in chunks of 5 and runs with a thread pool sized 5‑10. Adjust these values in `BatchConfig` or externalise them via properties as needed.

## Project structure

The code follows a conventional Maven layout; core packages under `com.team.imageprocessor` are:

```
src/main/java/com/team/imageprocessor
├── Application.java             # entry point (Spring Boot)
├── batch                       # Spring Batch reader/writer classes
│   ├── reader/ImageJobReader.java
│   └── writer/ImageJobWriter.java
├── config                      # Batch and executor configuration
│   └── BatchConfig.java
├── model                       # data transfer objects
│   └── ImageJob.java
├── processor                   # batch processor implementation
│   └── ImageJobProcessor.java
├── service                     # core business logic
│   └── ImageProcessingService.java
└── strategy                    # image‑filter implementations
    └── GrayscaleStrategy.java   # example strategy
```

Resources such as `application.properties` live in `src/main/resources` and hold Spring Batch/H2 defaults.

## Getting started

These instructions will get you a copy of the project running on your local machine for development and testing purposes.

### Prerequisites

- Java 21 or later (OpenJDK or Oracle)
- Maven 3.8+ installed and on `PATH`

### Build

```bash
git clone https://github.com/your-org/smart-bulk-image-processor.git
cd smart-bulk-image-processor
mvn clean package         # compiles code and runs unit tests
```

### Run

```bash
# development mode (recompiles on change)
mvn spring-boot:run

# or using the packaged JAR
target/smart-bulk-image-processor-0.0.1-SNAPSHOT.jar
java -jar target/smart-bulk-image-processor-0.0.1-SNAPSHOT.jar
```

Upon startup, the Spring Batch job is executed automatically. Use the log output to monitor progress.

### Usage

1. Copy `.jpg`, `.jpeg` or `.png` files into `images/input` at the project root. The directory and `images/output` are created if missing.
2. The application will detect and process files on the next job execution (at startup or when manually triggered).
3. Results are written to `images/output` with the same base filename; the original format is preserved.

## Configuration

The following parameters may be adjusted directly in source or externalised as Spring properties for greater flexibility.

| Parameter | Default | Location |
|-----------|---------|----------|
| Chunk size | `5` | `BatchConfig.imageStep` |
| Thread pool core size | `5` | `BatchConfig.threadPoolTaskExecutor` |
| Thread pool max size | `10` | same as above |
| Input directory | `images/input` | `ImageJobReader` |
| Output directory | `images/output` | `ImageJobReader` |

The application uses an embedded H2 database (`jdbc:h2:mem:testdb`) for Spring Batch metadata. Modify `src/main/resources/application.properties` if you need persistence or a different datasource.

## Extending the project

The architecture is deliberately extensible; common extension points are described below.

### Adding a new processing strategy

1. Implement the `ImageProcessingStrategy` interface.
2. Annotate the implementation with `@Component` or declare it as a Spring bean.
3. Update `ImageJobProcessor` to use the new strategy, either by injection or by strategy selection logic. Multiple strategies can be supported via `@Qualifier` or a `Map<String, ImageProcessingStrategy>`.

### Supporting additional file types

Enhance `ImageProcessingService.isImageFile` and `getFormat` to recognise new extensions (e.g. `.gif`, `.bmp`). Ensure the underlying `ImageIO` reader/writer supports the format.

## Troubleshooting

- **No images processed** – verify that supported files (.jpg, .jpeg, .png) are in `images/input`. Check log output for reader activity.
- **Job fails on startup** – consult the stack trace in the console. Common causes include unreadable or malformed image files.
- **Output folder not created** – file system permissions may prevent creation; ensure the process has write access to the project directory.

For additional issues, search the project’s issue tracker or raise a new issue with logs and reproduction steps.

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository and create a feature branch.
2. Run `mvn verify` to ensure tests pass.
3. Submit a pull request describing your changes.

Please adhere to Google's [Java Style Guide](https://google.github.io/styleguide/javaguide.html) and include unit tests for new features.
---

*Designed as part of the Image Processing Team’s graduation project; feel free to adapt for learning or prototyping.*
