package com.documind.service;

import com.documind.dto.response.RepoStatusResponse;
import com.documind.entity.Repo;
import com.documind.entity.RepoStatus;
import com.documind.event.RepoClonedEvent;
import com.documind.exception.RepoNotFoundException;
import com.documind.git.GitCloneException;
import com.documind.git.GitCloningService;
import com.documind.repository.RepoRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.util.UUID;

@Slf4j
@Service
public class RepoService {

    private final RepoRepository repoRepository;
    private final GitCloningService gitCloningService;
    private final ApplicationEventPublisher eventPublisher;

    public RepoService(RepoRepository repoRepository,
                       GitCloningService gitCloningService,
                       ApplicationEventPublisher eventPublisher) {
        this.repoRepository = repoRepository;
        this.gitCloningService = gitCloningService;
        this.eventPublisher = eventPublisher;
    }

    @Async("cloneTaskExecutor")
    public void cloneRepositoryAsync(UUID repoId) {
        Repo repo = repoRepository.findById(repoId)
                .orElseThrow(() -> new IllegalStateException("Repo not found: " + repoId));

        repo.setStatus(RepoStatus.CLONING);
        repoRepository.save(repo);

        try {
            Path clonedPath = gitCloningService.cloneRepository(
                    repo.getUrl(),
                    repoId.toString()
            );

            repo.setLocalPath(clonedPath.toString());
            repo.setStatus(RepoStatus.CLONED);
            repoRepository.save(repo);

            eventPublisher.publishEvent(new RepoClonedEvent(this, repoId));

        }
        catch (GitCloneException e) {
            log.error("Clone failed for repo {}: {}", repoId, e.getMessage());
            repo.setStatus(RepoStatus.FAILED);
            repo.setFailureReason(e.getMessage());
            repoRepository.save(repo);
        }
    }

    public RepoStatusResponse toResponse(Repo repo) {
        return RepoStatusResponse.builder()
                .id(repo.getId())
                .url(repo.getUrl())
                .name(repo.getName())
                .status(repo.getStatus())
                .failureReason(repo.getFailureReason())
                .createdAt(repo.getCreatedAt())
                .updatedAt(repo.getUpdatedAt())
                .build();
    }


    public RepoStatusResponse createRepo(String url) {
        Repo repo = new Repo();
        repo.setUrl(url);
        repo.setName(extractRepoName(url));
        repo.setStatus(RepoStatus.PENDING);

        Repo saved = repoRepository.save(repo);

        cloneRepositoryAsync(saved.getId());

        return toResponse(saved);
    }

    public RepoStatusResponse getStatus(UUID repoId) {
        Repo repo = repoRepository.findById(repoId)
                .orElseThrow(() -> new RepoNotFoundException(repoId));
        return toResponse(repo);
    }

    private String extractRepoName(String url) {
        String cleaned = url.replaceAll("/$", "").replaceAll("\\.git$", "");
        String[] parts = cleaned.split("/");
        return parts[parts.length - 1];
    }
}