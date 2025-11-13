# JAX Image Tools (JIT) Python API

## Introduction
The pyjit package contains code common to JAX Image Tools (JIT), mostly DL and AI tools.
There are common dao packages which each tool consumes to reduce code copying.
This package reduces code duplication between the temporal.io workers which are part of JIT.

## Quick Start
### Install

poetry add jax-pyjit


### Usage for Common Tools
Data Access Object Example
```
from jax.pyjit.dao import StorageKey
```
This provides an easy way to create json objects used with the JIT server.

### Usage of JIT Client
jax-pyjit will also contain a requests-based client one day similar to the JIT Shell.



