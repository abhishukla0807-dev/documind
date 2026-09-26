package com.documind.repository;

import com.documind.entity.Repo;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface RepoRepository extends JpaRepository<Repo, UUID> {
}