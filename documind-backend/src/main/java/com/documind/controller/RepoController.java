package com.documind.controller;

import com.documind.dto.request.RepoRequest;
import com.documind.dto.response.RepoStatusResponse;
import com.documind.service.RepoService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/api/repos")
public class RepoController {

    private final RepoService repoService;

    public RepoController(RepoService repoService) {
        this.repoService = repoService;
    }

    @PostMapping
    public ResponseEntity<RepoStatusResponse> submitRepo(@Valid @RequestBody RepoRequest request) {
        RepoStatusResponse response = repoService.createRepo(request.getUrl());
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(response);
    }

    @GetMapping("/{id}/status")
    public ResponseEntity<RepoStatusResponse> getStatus(@PathVariable UUID id) {
        RepoStatusResponse response = repoService.getStatus(id);
        return ResponseEntity.ok(response);
    }
}