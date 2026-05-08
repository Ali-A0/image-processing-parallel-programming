package com.team.imageprocessor.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.awt.image.BufferedImage;
import java.nio.file.Path;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ImageJob {
    private String fileName;
    private Path inputPath;
    private Path outputPath;
    private BufferedImage processedImage;
}

