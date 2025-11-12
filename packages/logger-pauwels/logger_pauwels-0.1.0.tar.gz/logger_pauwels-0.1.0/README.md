# Python-Logger
Logger for python that can write into stdout, create a log file at the end.

## Usage

**You can have diferent types of logs:**

- log, normal logs
- warn
- error
- debug, can be disabled with parameter self.debug (`debug=False` in constructor)

- success
- failed


**You also have different kind of layout functions:**

- `section`, create a separation to arrange your logs

```
................................. SECTION .................................
```

- `cadre`, create a rectangle with text inside

```
################################################################################
#                                                                              #
#                                                                              #
#                                    CADRE                                     #
#                                                                              #
#                                                                              #
################################################################################
```


**Macros to start and finish your logs are here to help you:**

- `init`, Create a cadre and start timer
- `end`, stop timer, create a last log with total duration and save into file