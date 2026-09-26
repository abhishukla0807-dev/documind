package com.documind.event;

import lombok.Getter;
import org.springframework.context.ApplicationEvent;

import java.util.UUID;

@Getter
public class RepoClonedEvent extends ApplicationEvent {

    private final UUID repoId;

    public RepoClonedEvent(Object source, UUID repoId) {
        super(source);
        this.repoId = repoId;
    }
}