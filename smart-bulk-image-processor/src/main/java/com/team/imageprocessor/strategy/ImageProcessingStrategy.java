package com.team.imageprocessor.strategy;

import java.awt.image.BufferedImage;

public interface ImageProcessingStrategy {
    BufferedImage process(BufferedImage source);
    String getFilterName();
}
