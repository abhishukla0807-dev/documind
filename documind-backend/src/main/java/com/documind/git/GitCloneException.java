package com.documind.git;

public class GitCloneException extends RuntimeException {

    public GitCloneException(String message, Throwable cause) {
        super(message, cause);
    }

    public GitCloneException(String message) {
        super(message);
    }
}