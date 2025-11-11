# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.2.0] - 2025-11-11

## Added

Added a `timeout` context manager, which can be used to limit the execution time of a
block of code. If the block exceeds the specified time limit, a `TimeoutError` is
raised.

## [v0.1.0] - 2025-11-10

## Added

- Initial release of the project, which includes the utility functions
  `cache_arguments`, `no_terminal_output` and `only_allow_specific_loggers`.
