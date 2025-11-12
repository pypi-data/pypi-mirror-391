# Changelog

## 2.0.2 (2025-11-11)

Full Changelog: [v2.0.1...v2.0.2](https://github.com/sudoping01/djelia-sdk/compare/v2.0.1...v2.0.2)

### Bug Fixes

* compat with Python 3.14 ([76d8281](https://github.com/sudoping01/djelia-sdk/commit/76d82814f7f766674dd6712de2fdfd0389ba533b))


### Chores

* **internal:** grammar fix (it's -&gt; its) ([1251812](https://github.com/sudoping01/djelia-sdk/commit/1251812b7734204145b2bd7b1e25faeddbb8fde8))
* **package:** drop Python 3.8 support ([b5b6a6d](https://github.com/sudoping01/djelia-sdk/commit/b5b6a6dfedd415633b02f4de3cd6a44fca1aa4fb))

## 2.0.1 (2025-10-31)

Full Changelog: [v2.0.0...v2.0.1](https://github.com/sudoping01/djelia-sdk/compare/v2.0.0...v2.0.1)

### Bug Fixes

* **ci:** ensure pip is always available ([#15](https://github.com/sudoping01/djelia-sdk/issues/15)) ([4fa33f4](https://github.com/sudoping01/djelia-sdk/commit/4fa33f48f5f48dd9ef695a8599fd910e61af7655))
* **ci:** remove publishing patch ([#17](https://github.com/sudoping01/djelia-sdk/issues/17)) ([587c49d](https://github.com/sudoping01/djelia-sdk/commit/587c49dbdab201b82ee2a2566798f28ac6e903fb))
* **package:** support direct resource imports ([61a81f4](https://github.com/sudoping01/djelia-sdk/commit/61a81f40574bffcf90ef43a7e42ae863b513c8d9))
* **perf:** optimize some hot paths ([8d82ee9](https://github.com/sudoping01/djelia-sdk/commit/8d82ee9d21c6381bd604b04f92ecf8ec85227d2b))
* **perf:** skip traversing types for NotGiven values ([31b6a6b](https://github.com/sudoping01/djelia-sdk/commit/31b6a6b3ae20a0af4b2df859e0aaf243964145e1))
* **pydantic v1:** more robust ModelField.annotation check ([3cbbb83](https://github.com/sudoping01/djelia-sdk/commit/3cbbb838b1cfb698c10de09b0dc01c5f4b458a53))


### Chores

* broadly detect json family of content-type headers ([6e3053b](https://github.com/sudoping01/djelia-sdk/commit/6e3053b9d1036bf134bc6b0aa8b8efbe538a84a7))
* **ci:** add timeout thresholds for CI jobs ([2836802](https://github.com/sudoping01/djelia-sdk/commit/2836802205d9d4b99367b16e7f1c4c9f047cd893))
* **ci:** only use depot for staging repos ([d2a70fd](https://github.com/sudoping01/djelia-sdk/commit/d2a70fdd16e50c681ce65617add326b63457ccfb))
* **client:** minor internal fixes ([ffa4e81](https://github.com/sudoping01/djelia-sdk/commit/ffa4e81710a77684000b826b2a8bef513b03aa9c))
* fix typos ([#18](https://github.com/sudoping01/djelia-sdk/issues/18)) ([b8a135e](https://github.com/sudoping01/djelia-sdk/commit/b8a135eacc1edb875ea425a0ce63dadb3502bca3))
* **internal:** avoid errors for isinstance checks on proxies ([0eae842](https://github.com/sudoping01/djelia-sdk/commit/0eae84271c3249583e6cb6e6fe382a0dc7bd1c5c))
* **internal:** base client updates ([7cf7146](https://github.com/sudoping01/djelia-sdk/commit/7cf71467cb8902387d59e3108d38e9a6db367cac))
* **internal:** bump pyright version ([78eff09](https://github.com/sudoping01/djelia-sdk/commit/78eff0951ea23486cd69c74a052ff4025da5a64f))
* **internal:** codegen related update ([f2398e3](https://github.com/sudoping01/djelia-sdk/commit/f2398e322ee5b8bc93f681e945eee01169b61f88))
* **internal:** codegen related update ([e500eb9](https://github.com/sudoping01/djelia-sdk/commit/e500eb9911bb8a08d8790908f16fa121dc02de6b))
* **internal:** codegen related update ([28eb30f](https://github.com/sudoping01/djelia-sdk/commit/28eb30f6b3ff36f0c4891ea8d58f834c8eb4c817))
* **internal:** codegen related update ([e222aa7](https://github.com/sudoping01/djelia-sdk/commit/e222aa755a66cb9485d82f63ab7a722a2646b6d6))
* **internal:** codegen related update ([d85d835](https://github.com/sudoping01/djelia-sdk/commit/d85d83590f656e37b4f579e6607f716079fd9f22))
* **internal:** codegen related update ([853aa8e](https://github.com/sudoping01/djelia-sdk/commit/853aa8eb72445084d9bf34b7c887f98890b2f940))
* **internal:** expand CI branch coverage ([cb138d5](https://github.com/sudoping01/djelia-sdk/commit/cb138d5cd55716828fda795dc50fcaa542acd7f0))
* **internal:** fix list file params ([e7cadc8](https://github.com/sudoping01/djelia-sdk/commit/e7cadc84be2c90f1242d600cef324d7ca8a460d1))
* **internal:** import reformatting ([232c8d6](https://github.com/sudoping01/djelia-sdk/commit/232c8d6d5f4aa92b35266cdd6da6445f97693721))
* **internal:** minor formatting changes ([16ecae5](https://github.com/sudoping01/djelia-sdk/commit/16ecae5b9e029f36d6389d2193653e389b4a8104))
* **internal:** reduce CI branch coverage ([9797d47](https://github.com/sudoping01/djelia-sdk/commit/9797d47b81a3809c3650b49a64ce08e7cba19678))
* **internal:** refactor retries to not use recursion ([39e1237](https://github.com/sudoping01/djelia-sdk/commit/39e123735133c45c1dfe67bfddb60d452be37772))
* **internal:** remove trailing character ([#19](https://github.com/sudoping01/djelia-sdk/issues/19)) ([d7cab9b](https://github.com/sudoping01/djelia-sdk/commit/d7cab9bc3b69e176911223bf51229ee59da28b41))
* **internal:** slight transform perf improvement ([#20](https://github.com/sudoping01/djelia-sdk/issues/20)) ([ba61667](https://github.com/sudoping01/djelia-sdk/commit/ba61667890d587ae3748123045fe3ad6e73ce82d))
* **internal:** update models test ([4a1c643](https://github.com/sudoping01/djelia-sdk/commit/4a1c64361c9361781667cfde23cbe654c99aa4ca))
* **internal:** update pyright settings ([72bb640](https://github.com/sudoping01/djelia-sdk/commit/72bb6409a1882f06f49c48fcdc706fb3c245d612))
* slight wording improvement in README ([#21](https://github.com/sudoping01/djelia-sdk/issues/21)) ([6a57c4d](https://github.com/sudoping01/djelia-sdk/commit/6a57c4d763e5ab93eba6a08d64f5addc862ba402))

## 2.0.0 (2025-03-15)

Full Changelog: [v1.0.0...v2.0.0](https://github.com/sudoping01/djelia-sdk/compare/v1.0.0...v2.0.0)

### Bug Fixes

* **types:** handle more discriminated union shapes ([#13](https://github.com/sudoping01/djelia-sdk/issues/13)) ([7eec71a](https://github.com/sudoping01/djelia-sdk/commit/7eec71ab44c5f5eeef402dc78ef19f19759d684c))


### Chores

* **internal:** bump rye to 0.44.0 ([#12](https://github.com/sudoping01/djelia-sdk/issues/12)) ([857af0c](https://github.com/sudoping01/djelia-sdk/commit/857af0c1136335820a2d035e2ec7f04cea583907))
* **internal:** codegen related update ([#11](https://github.com/sudoping01/djelia-sdk/issues/11)) ([b97a8fb](https://github.com/sudoping01/djelia-sdk/commit/b97a8fbf64a31ffe51b119f8612549822dc6ff28))
* **internal:** remove extra empty newlines ([#10](https://github.com/sudoping01/djelia-sdk/issues/10)) ([4886a59](https://github.com/sudoping01/djelia-sdk/commit/4886a59685a417c2877b27b29c2e5dc87d7caf2d))

## 1.0.0 (2025-03-04)

Full Changelog: [v0.0.1-alpha.1...v1.0.0](https://github.com/sudoping01/djelia-sdk/compare/v0.0.1-alpha.1...v1.0.0)

### Chores

* **internal:** remove unused http client options forwarding ([#5](https://github.com/sudoping01/djelia-sdk/issues/5)) ([97ae641](https://github.com/sudoping01/djelia-sdk/commit/97ae64152cae5bcc43292dfb3c1c82984c843189))

## 0.0.1-alpha.1 (2025-03-02)

Full Changelog: [v0.0.1-alpha.0...v0.0.1-alpha.1](https://github.com/sudoping01/djelia-sdk/compare/v0.0.1-alpha.0...v0.0.1-alpha.1)

### Chores

* go live ([#1](https://github.com/sudoping01/djelia-sdk/issues/1)) ([91e114f](https://github.com/sudoping01/djelia-sdk/commit/91e114faf946bda753ac0aa96228818a7ff11652))
* update SDK settings ([#3](https://github.com/sudoping01/djelia-sdk/issues/3)) ([720c389](https://github.com/sudoping01/djelia-sdk/commit/720c38966654198bd9abe8a5695c197bc63e7813))
