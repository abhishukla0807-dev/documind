package com.documind.dto.response;

import com.documind.entity.RepoStatus;
import lombok.Builder;
import lombok.Getter;

import java.time.OffsetDateTime;
import java.util.UUID;

@Getter
@Builder
public class RepoStatusResponse {

    private UUID id;
    private String url;
    private String name;
    private RepoStatus status;
    private String failureReason;
    private OffsetDateTime createdAt;
    private OffsetDateTime updatedAt;
}