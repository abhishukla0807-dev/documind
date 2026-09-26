package com.documind.git;

import java.nio.file.Path;

public interface GitCloningService {
    Path cloneRepository(String repoUrl, String destinationFolderName) throws GitCloneException;
}