# EGNOSTools


This is a set of support tools for EGNOS processing. Relevant documentation is in the .\docs folder


* `RINEXb2EMS.py` is a converter from RINEX b to EGNOS EMS format
	* SBAS B specs are in .\docs\geo_sbas.txt 
	* [ESA EMS2.0](http://www.egnos-pro.esa.int/ems/index.html) can be found at <ftp://ems.estec.esa.int/pub/> and <https://ntmf.cnes.fr/web-ntmf/public/home>
* `RTKLibStatusDecoder.py` is a visualisation tool for the RTKLib status file
	* plots residuals from $SAT string, split by SV and overall residual values per SV