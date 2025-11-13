Flask v1.0
=====

A patch of the [v1.0 2019 version](https://pypi.org/project/Flask/1.0/)
of [Flask](https://pypi.org/project/Flask/), with working dependency ranges.

Why?
---

As of 12th November 2025, [Flask v1.0.x](https://github.com/pallets/flask/tree/1.0.x)
unfortunately doesn't set any upper bounds for its dependencies. This means that simply
running `pip install flask<1.0` will pull down the latest version of all of its dependencies.
The latest versions of a couple of these packages now have significant changes which break
Flask v1.0's usage of them.

What?
---

I tested Flask v1.0.4 with the Python versions `3.7` and `3.14`.

Only the following packages needed constraining:

- `Werkzeug<3`
- `Jinja2<3.1`
- `itsdangerous< 2.1`
