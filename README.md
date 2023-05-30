# metapipeline

Python package to build functions pipeline and create automatic parameter grid search.

## Usage

Usage example in the `example` folder

- Create pipeline of several functions. Each step is an objet that store its intermediate output
- Accessing a given step output in the pipeline will compute all previous necessary steps
- User can define parameter to explore for a given pipeline using the ListParam object
