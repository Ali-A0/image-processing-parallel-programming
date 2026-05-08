package com.team.imageprocessor.config;

import com.team.imageprocessor.batch.reader.ImageJobReader;
import com.team.imageprocessor.batch.writer.ImageJobWriter;
import com.team.imageprocessor.model.ImageJob;
import com.team.imageprocessor.processor.ImageJobProcessor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.batch.core.Job;
import org.springframework.batch.core.Step;
import org.springframework.batch.core.job.builder.JobBuilder;
import org.springframework.batch.core.repository.JobRepository;
import org.springframework.batch.core.step.builder.StepBuilder;
import org.springframework.batch.item.ItemReader;
import org.springframework.batch.item.support.ListItemReader;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.task.TaskExecutor;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;
import org.springframework.transaction.PlatformTransactionManager;

@Slf4j
@Configuration
public class BatchConfig {

    @Bean
    public ItemReader<ImageJob> imageReader(ImageJobReader readerService) {
        ListItemReader<ImageJob> delegate = new ListItemReader<>(readerService.readInputImages());
        return () -> {
            synchronized (delegate) {
                return delegate.read();
            }
        };
    }

    @Bean
    public TaskExecutor threadPoolTaskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setThreadNamePrefix("ImgProc-");
        executor.initialize();
        return executor;
    }

    @Bean
    public Step imageStep(JobRepository jobRepository, PlatformTransactionManager transactionManager,
                         ItemReader<ImageJob> imageReader, ImageJobProcessor processor, ImageJobWriter writer,
                         TaskExecutor threadPoolTaskExecutor) {
        return new StepBuilder("imageStep", jobRepository)
                .<ImageJob, ImageJob>chunk(5, transactionManager)
                .reader(imageReader)
                .processor(processor)
                .writer(writer)
                .taskExecutor(threadPoolTaskExecutor)
                .build();
    }

    @Bean
    public Job imageJob(JobRepository jobRepository, Step imageStep) {
        return new JobBuilder("imageJob", jobRepository)
                .start(imageStep)
                .build();
    }
}


