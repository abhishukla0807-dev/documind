package com.documind.git;

import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
public class JGitCloningService implements GitCloningService {

    private final String baseClonePath;

    public JGitCloningService(@Value("${documind.clone.base-path}") String baseClonePath) {
        this.baseClonePath = baseClonePath;
    }

    @Override
    public Path cloneRepository(String repoUrl, String destinationFolderName) {
        Path targetPath = Paths.get(baseClonePath, destinationFolderName);
        File targetDir = targetPath.toFile();

        try
        {
            Git.cloneRepository()
                    .setURI(repoUrl)
                    .setDirectory(targetDir)
                    .setDepth(1)
                    .call();

            return targetPath;

        }

        catch (GitAPIException e) {
            throw new GitCloneException(
                    "Failed to clone repository: " + repoUrl, e
            );
        }
    }
}