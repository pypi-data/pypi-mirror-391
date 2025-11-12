# Changelog

## 0.7.2 (2025-11-12)

Full Changelog: [v0.7.1...v0.7.2](https://github.com/aiinbx/aiinbx-py/compare/v0.7.1...v0.7.2)

### Bug Fixes

* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([63fdaba](https://github.com/aiinbx/aiinbx-py/commit/63fdaba20d9bfe35d1d1358ef229d28c222b5ecf))

## 0.7.1 (2025-11-11)

Full Changelog: [v0.7.0...v0.7.1](https://github.com/aiinbx/aiinbx-py/compare/v0.7.0...v0.7.1)

### Bug Fixes

* compat with Python 3.14 ([17da3dd](https://github.com/aiinbx/aiinbx-py/commit/17da3dd00711f92f515ab05562b79eb784d0ce24))


### Chores

* **internal:** codegen related update ([2976852](https://github.com/aiinbx/aiinbx-py/commit/2976852cdedba8ffdaed6879fd51d87708419503))

## 0.7.0 (2025-11-04)

Full Changelog: [v0.6.0...v0.7.0](https://github.com/aiinbx/aiinbx-py/compare/v0.6.0...v0.7.0)

### Features

* **api:** api update ([0f82ed1](https://github.com/aiinbx/aiinbx-py/commit/0f82ed1bf1a6d34c2e63ecbc9cf0a5b43f53e89a))


### Chores

* **internal:** grammar fix (it's -&gt; its) ([4398c76](https://github.com/aiinbx/aiinbx-py/commit/4398c76c2f4f5cd115df6f40f9948dc9d439a9b6))

## 0.6.0 (2025-10-31)

Full Changelog: [v0.5.1...v0.6.0](https://github.com/aiinbx/aiinbx-py/compare/v0.5.1...v0.6.0)

### Features

* **api:** api update ([e0ee97a](https://github.com/aiinbx/aiinbx-py/commit/e0ee97a7568dc6839f1c011b5312ec34ce3d9f7d))


### Chores

* **internal/tests:** avoid race condition with implicit client cleanup ([4cf6938](https://github.com/aiinbx/aiinbx-py/commit/4cf6938564097419455a6219e0b217e7921a9ea2))

## 0.5.1 (2025-10-30)

Full Changelog: [v0.5.0...v0.5.1](https://github.com/aiinbx/aiinbx-py/compare/v0.5.0...v0.5.1)

### Bug Fixes

* **client:** close streams without requiring full consumption ([d824bbb](https://github.com/aiinbx/aiinbx-py/commit/d824bbbd517355748039bf7f5edfbee0e802a606))


### Chores

* bump `httpx-aiohttp` version to 0.1.9 ([8c932fb](https://github.com/aiinbx/aiinbx-py/commit/8c932fb49aa74fe9174deb5c7b4e71cccd41f119))

## 0.5.0 (2025-10-15)

Full Changelog: [v0.4.0...v0.5.0](https://github.com/aiinbx/aiinbx-py/compare/v0.4.0...v0.5.0)

### Features

* **api:** manual updates ([ddacc81](https://github.com/aiinbx/aiinbx-py/commit/ddacc8158fd4079c1ee4b8ae04f89f22e2fcd46a))


### Chores

* **internal:** detect missing future annotations with ruff ([6f6a3da](https://github.com/aiinbx/aiinbx-py/commit/6f6a3da5978b34e1a2959b38715d4311474f1c5e))

## 0.4.0 (2025-10-05)

Full Changelog: [v0.3.0...v0.4.0](https://github.com/aiinbx/aiinbx-py/compare/v0.3.0...v0.4.0)

### Features

* **api:** manual updates ([601d5ea](https://github.com/aiinbx/aiinbx-py/commit/601d5eade9216549a200c26584a2cc18176835fd))
* improve future compat with pydantic v3 ([dcc1c80](https://github.com/aiinbx/aiinbx-py/commit/dcc1c804ec998e7948395f7c1ea3aac371a539fb))
* **types:** replace List[str] with SequenceNotStr in params ([a31a999](https://github.com/aiinbx/aiinbx-py/commit/a31a999a8dd553a067fdd4368d147f773418dc02))


### Chores

* do not install brew dependencies in ./scripts/bootstrap by default ([b4c08e3](https://github.com/aiinbx/aiinbx-py/commit/b4c08e37dfa25b784a2cd7d5e9778f3318c365b9))
* **internal:** add Sequence related utils ([879c21a](https://github.com/aiinbx/aiinbx-py/commit/879c21ac262c2c10c0e1bfa03d5d1c40470f889b))
* **internal:** move mypy configurations to `pyproject.toml` file ([3108a79](https://github.com/aiinbx/aiinbx-py/commit/3108a794e35f868d1e21a210abbda837eecc64d1))
* **internal:** update pydantic dependency ([6dcd694](https://github.com/aiinbx/aiinbx-py/commit/6dcd694e2ab6b8246892ebef85e95bff9b0338a9))
* **tests:** simplify `get_platform` test ([0f14d8c](https://github.com/aiinbx/aiinbx-py/commit/0f14d8cd43342f3fda7ccda30717c01d20679593))
* **types:** change optional parameter type from NotGiven to Omit ([1b12faa](https://github.com/aiinbx/aiinbx-py/commit/1b12faa48dbcc8fedf5dc8e4a410c58fcfac7853))

## 0.3.0 (2025-08-28)

Full Changelog: [v0.2.0...v0.3.0](https://github.com/aiinbx/aiinbx-py/compare/v0.2.0...v0.3.0)

### Features

* **api:** api update ([2de3cb7](https://github.com/aiinbx/aiinbx-py/commit/2de3cb73d4178e81925fd6d04b3683b81e7da30d))

## 0.2.0 (2025-08-28)

Full Changelog: [v0.1.1...v0.2.0](https://github.com/aiinbx/aiinbx-py/compare/v0.1.1...v0.2.0)

### Features

* **api:** manual updates ([f4e60fe](https://github.com/aiinbx/aiinbx-py/commit/f4e60fed47de83248dbcef3cd28590643c0b9bff))

## 0.1.1 (2025-08-27)

Full Changelog: [v0.1.0...v0.1.1](https://github.com/aiinbx/aiinbx-py/compare/v0.1.0...v0.1.1)

### Bug Fixes

* avoid newer type syntax ([85f2191](https://github.com/aiinbx/aiinbx-py/commit/85f21914439dbd7e3ef751a1010eaf023b33ef70))


### Chores

* **internal:** change ci workflow machines ([7e210c5](https://github.com/aiinbx/aiinbx-py/commit/7e210c590a8a7659cbbf3f087b869ca580bd9b1b))
* **internal:** update pyright exclude list ([a4d4c96](https://github.com/aiinbx/aiinbx-py/commit/a4d4c9626f42577c535516072216bc82c6b2d551))
* update github action ([d06abee](https://github.com/aiinbx/aiinbx-py/commit/d06abee5f995ce020da7ab44160eaab348c8c18a))

## 0.1.0 (2025-08-13)

Full Changelog: [v0.0.1...v0.1.0](https://github.com/aiinbx/aiinbx-py/compare/v0.0.1...v0.1.0)

### Features

* **api:** manual updates ([9f338c0](https://github.com/aiinbx/aiinbx-py/commit/9f338c08cf76e9482a9529c761654cdd250483ea))


### Chores

* configure new SDK language ([3cc34fc](https://github.com/aiinbx/aiinbx-py/commit/3cc34fcf8b0325986076726a774c419992b5aafa))
* update SDK settings ([9251ee7](https://github.com/aiinbx/aiinbx-py/commit/9251ee7b47185255692e59f672e6158f4af32541))
