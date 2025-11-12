# Changelog

All notable changes to the RBFM-VAR package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-11

### Added
- Initial release of RBFM-VAR package
- Core RBFM-VAR estimator implementing Chang (2000)
- Kernel-based long-run covariance estimation with four kernel options
- Modified Wald test for hypothesis testing (Theorem 2)
- Granger causality testing in nonstationary VARs
- Automatic lag order selection via information criteria
- Multi-step ahead forecasting
- Comprehensive diagnostic tests (Portmanteau, ARCH, stability)
- Example scripts including simulation study replicating paper results
- Complete documentation (README, USER_GUIDE, docstrings)
- MIT License

### Features
- **Estimation**: RBFM-VAR with corrections for endogeneity and serial correlation
- **Testing**: Modified Wald tests with conservative chi-square critical values
- **Kernels**: Bartlett, Parzen, Quadratic Spectral, Tukey-Hanning
- **Bandwidth**: Automatic selection using Andrews (1991) method
- **Diagnostics**: Residual autocorrelation, ARCH effects, stability checks
- **Examples**: Simple example and Monte Carlo simulation study

### Implementation Details
- Follows Chang (2000) equations exactly
- Handles I(0), I(1), and I(2) processes automatically
- No pretesting required for unit roots or cointegration
- Uses Moore-Penrose inverse for numerical stability
- Comprehensive error handling and warnings

### Documentation
- README.md: Package overview and quick start
- USER_GUIDE.md: Detailed usage instructions
- IMPLEMENTATION_NOTES.md: Technical implementation details
- Docstrings: Every function and class documented
- Examples: Two complete example scripts

### Testing
- test_installation.py: Comprehensive installation verification
- Validates all major functionality

## [Unreleased]

### Planned Features
- [ ] Unit test suite with pytest
- [ ] Confidence intervals for forecasts
- [ ] Impulse response functions (IRFs)
- [ ] Forecast error variance decomposition (FEVD)
- [ ] Support for deterministic trends
- [ ] Exogenous variables handling
- [ ] Panel VAR extension
- [ ] Bayesian RBFM-VAR
- [ ] Additional diagnostic plots
- [ ] Performance optimizations for large systems

### Known Issues
- None reported yet

## Notes

### Version 1.0.0 Scope

This initial release focuses on core functionality exactly as specified in Chang (2000):
- Equation (3): Model reformulation
- Equations (12-13): RBFM-VAR estimator
- Equation (20): Modified Wald test
- Section 5: Monte Carlo simulations

All core features from the paper are implemented and validated.

### Future Development

We welcome contributions! Areas for future development include:
1. Extended hypothesis testing options
2. Additional diagnostic tools
3. Visualization enhancements
4. Performance optimizations
5. Integration with other econometric packages

### Feedback

Please report bugs and request features via:
- GitHub Issues: https://github.com/merwanroudane/RBFMVAR/issues
- Email: merwanroudane920@gmail.com

---

**Maintainer:** Dr. Merwan Roudane  
**Repository:** https://github.com/merwanroudane/RBFMVAR  
**License:** MIT
