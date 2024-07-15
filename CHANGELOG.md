# CHANGELOG

## Version 4.0.3
* Added CLI support (using Click)

### TODO
* Add in support for [ProxyScrape](https://proxyscrape.com/)

## Version 3.1.1
* Refactored and tidied up.
* get backwards compatibility for `get_first_operational_proxy()`

## Version 2.2.0
 * Added in support for [SpeedX Proxy List](https://github.com/TheSpeedX/PROXY-List)
 * Added randomisation of proxy list order in get_first_operational_proxy()

## Version 2.1.2
 Updated to use urllib3 1.26.13 - NB: This is required.


## Version 2.1.1
### Major Changes
Restructured to keep the primary funcionality available at the top level.  Now `get_first_operational_proxy()` simply returns this, with optional `filter_by` parameter.  See README for more details.

