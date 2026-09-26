package com.documind.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RepoRequest {

    @NotBlank(message = "Repository URL is required")
    @Pattern(
            regexp = "^(https?://).+\\.git$|^(https?://)(www\\.)?github\\.com/.+$",
            message = "Must be a valid Git repository URL"
    )
    private String url;
}