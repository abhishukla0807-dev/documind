package com.documind.event;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

@Slf4j
@Component
public class RepoEventListener {

    @EventListener
    public void handleRepoCloned(RepoClonedEvent event) {
        log.info("Repo cloned successfully. Repo ID: {}", event.getRepoId());
        // Phase 2 me yaha ingestion trigger hoga
    }
}