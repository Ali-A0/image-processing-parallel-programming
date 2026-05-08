package com.team.imageprocessor.strategy;

import java.awt.*;
import java.awt.image.BufferedImage;
import org.springframework.stereotype.Component;

@Component
public class GrayscaleStrategy implements ImageProcessingStrategy {
    @Override
    public BufferedImage process(BufferedImage source) {
        BufferedImage grayImage = new BufferedImage(source.getWidth(), source.getHeight(), BufferedImage.TYPE_BYTE_GRAY);
        Graphics g = grayImage.getGraphics();
        g.drawImage(source, 0, 0, null);
        g.dispose();
        return grayImage;
    }

    @Override
    public String getFilterName() {
        return "grayscale";
    }
}
