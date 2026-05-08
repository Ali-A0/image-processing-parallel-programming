package com.team.imageprocessor.service;

import com.team.imageprocessor.strategy.ImageProcessingStrategy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@Slf4j
@Service
@RequiredArgsConstructor
public class ImageProcessingService {

    public BufferedImage process(Path inputPath, ImageProcessingStrategy strategy) throws IOException {
        log.debug("Reading image from: {}", inputPath.toAbsolutePath());
        BufferedImage source = ImageIO.read(inputPath.toFile());
        if (source == null) {
            throw new IOException("Failed to decode image (returned null): " + inputPath.getFileName());
        }
        return strategy.process(source);
    }

    public void save(BufferedImage image, Path outputPath, String format) throws IOException {
        Path parent = outputPath.getParent();
        if (parent != null && !Files.exists(parent)) {
            Files.createDirectories(parent);
        }
        
        log.debug("Saving image to: {}", outputPath.toAbsolutePath());
        boolean success = ImageIO.write(image, format, outputPath.toFile());
        if (!success) {
            throw new IOException("ImageIO.write returned false for format: " + format);
        }
    }

    public boolean isImageFile(Path path) {
        String name = path.getFileName().toString().toLowerCase();
        return name.endsWith(".jpg") || name.endsWith(".jpeg") || name.endsWith(".png");
    }

    public String getFormat(String fileName) {
        return fileName.toLowerCase().endsWith(".png") ? "png" : "jpg";
    }
}


