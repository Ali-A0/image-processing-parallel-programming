package com.team.imageprocessor.batch.reader;

import com.team.imageprocessor.model.ImageJob;
import com.team.imageprocessor.service.ImageProcessingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.stream.Stream;

@Slf4j
@Service
@RequiredArgsConstructor
public class ImageJobReader {

    private final ImageProcessingService processingService;

    public List<ImageJob> readInputImages() {
        Path root = Paths.get("C:\\Users\\alima\\OneDrive\\Desktop\\Parallel\\").toAbsolutePath();
        Path inputFolder = root.resolve("images").resolve("input");
        Path outputFolder = root.resolve("images").resolve("output");
        
        log.info("Scanning for images in: {}", inputFolder);
        List<ImageJob> jobs = new CopyOnWriteArrayList<>();
        try {
            Files.createDirectories(inputFolder);
            Files.createDirectories(outputFolder);

            try (Stream<Path> paths = Files.list(inputFolder)) {
                paths.filter(Files::isRegularFile)
                     .filter(processingService::isImageFile)
                     .forEach(p -> {
                         String fileName = p.getFileName().toString();
                         jobs.add(ImageJob.builder()
                                 .fileName(fileName)
                                 .inputPath(p.toAbsolutePath())
                                 .outputPath(outputFolder.resolve(fileName).toAbsolutePath())
                                 .build());
                     });
            }
        } catch (Exception e) {
            log.error("Error scanning input directory: {}", e.getMessage(), e);
        }

        log.info("Found {} images to process", jobs.size());
        return jobs;
    }
}


