# Change Log

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]

### Added
- Implement simulate command line utility (from @justjasongreen)
- Implement predict command line utility (from @justjasongreen)


## [1.0.0a4] - 2016-07-29

### Fixed
- Fix TypeError in Race.calculate_value (from @justjasongreen)


## [1.0.0a3] - 2016-07-29

### Fixed
- Fix NameError when invoking seed command line utility (from @justjasongreen)


## [1.0.0a2] - 2016-07-29

### Added
- Extend racing_data.Race objects with an active_runners property (from @justjasongreen)
- Extend racing_data.Race objects with a get_winning_combinations method (from @justjasongreen)
- Extend racing_data.Race objects with a win_value property (from @justjasongreen)
- Extend racing_data.Race objects with an exacta_value property (from @justjasongreen)
- Extend racing_data.Race objects with a trifecta_value property (from @justjasongreen)
- Extend racing_data.Race objects with a first_four_value property (from @justjasongreen)
- Extend racing_data.Race objects with a total_value property (from @justjasongreen)
- Extend racing_data.Runner objects with a calculate_expected_times method (from @justjasongreen)
- Extend racing_data.Runner objects with a races_per_year property (from @justjasongreen)
- Add the Sample class (from @justjasongreen)
- Implement Provider.get_sample_by_runner method (from @justjasongreen)
- Extend racing_data.Race objects with a sample property (from @justjasongreen)
- Implement seed command line utility (from @justjasongreen)

### Changed
- Log the item associated with an exception in process_collection (from @justjasongreen)


## [1.0.0a1] - 2016-07-24

### Added
- Implement scrape command line utility (from @justjasongreen)


## [1.0.0a0] - 2016-07-22

### Added
- Set up project (from @justjasongreen)


[Unreleased]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a4...HEAD
[1.0.0a4]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a3...1.0.0a4
[1.0.0a3]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a2...1.0.0a3
[1.0.0a2]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a1...1.0.0a2
[1.0.0a1]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a0...1.0.0a1
[1.0.0a0]: https://github.com/justjasongreen/predictive_punter/tree/1.0.0a0
