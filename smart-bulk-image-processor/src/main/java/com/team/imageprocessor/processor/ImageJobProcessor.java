    package com.team.imageprocessor.processor;

    import com.team.imageprocessor.model.ImageJob;
    import com.team.imageprocessor.service.ImageProcessingService;
    import com.team.imageprocessor.strategy.ImageProcessingStrategy;
    import lombok.RequiredArgsConstructor;
    import lombok.extern.slf4j.Slf4j;
    import org.springframework.batch.item.ItemProcessor;
    import org.springframework.stereotype.Component;

    import java.awt.image.BufferedImage;
    import java.nio.file.Files;

    @Slf4j
    @Component
    @RequiredArgsConstructor
    public class ImageJobProcessor implements ItemProcessor<ImageJob, ImageJob> {

        private final ImageProcessingService processingService;
        private final ImageProcessingStrategy grayscaleStrategy;

        @Override
        public ImageJob process(ImageJob item) throws Exception {
            try {
                log.info("Processing file: {}", item.getFileName());

                if (!Files.exists(item.getInputPath())) {
                    log.error("Input file not found at: {}", item.getInputPath().toAbsolutePath());
                    return null;
                }

                BufferedImage processed = processingService.process(item.getInputPath(), grayscaleStrategy);
                item.setProcessedImage(processed);

                log.info("Successfully processed {} with strategy: {}", item.getFileName(), grayscaleStrategy.getFilterName());
                return item;
            } catch (Exception e) {
                log.error("CRITICAL ERROR processing {}: {}", item.getFileName(), e.getMessage(), e);
                throw e; 
            }
        }
    }



