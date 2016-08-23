# Datafreezer

Datafreezer is a newsroom tool that enables reporters and editors to easily share datasets.

## Features

#### Upload

- With each upload, users complete a data dictionary, which describes pertinent fields within a dataset. This ensures that uploaded datasets are well documented.
	- Users can either upload a dataset that already has header information, or they can add and remove data dictionary fields.
- Users can include a URL in which the data was sourced and the app will scrape the page for a headline to save.
- Tag support (with autocomplete)

#### Browse

- Users can browse datasets by
	- Uploading user
	- Hub (desk)
	- Vertical (section)
	- Tag
	- Source
- The app uses a pluggable JSON endpoint to map email addresses to names and certain slugs to names.
	- This endpoint can be a static JSON or an API.

## Credits
Thanks to [Glyphicons](http://glyphicons.com/) for Bootstrap glyphs.

Developed by [Tyler Davis](http://twitter.com/tylerallyndavis) for [The Dallas Morning News](http://dallasnews.com).
