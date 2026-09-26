package com.documind.exception;

import java.util.UUID;

public class RepoNotFoundException extends RuntimeException {
    public RepoNotFoundException(UUID repoId) {
        super("Repository not found with id: " + repoId);
    }
}