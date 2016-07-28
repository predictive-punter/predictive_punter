# Change Log

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased]

### Added
- Extend racing_data.Race objects with an active_runners property (from @justjasongreen)
- Extend racing_data.Race objects with a get_winning_combinations method (from @justjasongreen)
- Extend racing_data.Race objects with a win_value property (from @justjasongreen)
- Extend racing_data.Race objects with an exacta_value property (from @justjasongreen)
- Extend racing_data.Race objects with a trifecta_value property (from @justjasongreen)
- Extend racing_data.Runner objects with a calculate_expected_times method (from @justjasongreen)
- Extend racing_data.Runner objects with a races_per_year property (from @justjasongreen)

### Changed
- Log the item associated with an exception in process_collection (from @justjasongreen)


## [1.0.0a1] - 2016-07-24

### Added
- Implement scrape command line utility (from @justjasongreen)


## [1.0.0a0] - 2016-07-22

### Added
- Set up project (from @justjasongreen)


[Unreleased]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a1...HEAD
[1.0.0a1]: https://github.com/justjasongreen/predictive_punter/compare/1.0.0a0...1.0.0a1
[1.0.0a0]: https://github.com/justjasongreen/predictive_punter/tree/1.0.0a0
