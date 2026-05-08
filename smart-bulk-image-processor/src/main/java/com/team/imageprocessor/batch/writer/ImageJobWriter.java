package com.team.imageprocessor.batch.writer;

import com.team.imageprocessor.model.ImageJob;
import com.team.imageprocessor.service.ImageProcessingService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.item.Chunk;
import org.springframework.batch.item.ItemWriter;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ImageJobWriter implements ItemWriter<ImageJob> {

    private final ImageProcessingService processingService;

    @Override
    public void write(Chunk<? extends ImageJob> chunk) throws Exception {
        for (ImageJob item : chunk.getItems()) {
            if (item.getProcessedImage() != null) {
                try {
                    String format = processingService.getFormat(item.getFileName());
                    processingService.save(item.getProcessedImage(), item.getOutputPath(), format);
                    log.info("SAVED: {}", item.getFileName());
                } catch (Exception e) {
                    log.error("ERROR saving {}: {}", item.getFileName(), e.getMessage());
                }
            }
        }
    }
}
