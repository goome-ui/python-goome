<h1 align="center">🛠 Contributing to python-goome 🛠</h1>

<p align="center">
Thanks for wanting to help! Small PRs that fix one thing are the easiest for me to check and merge, so keep them small and theyll get in way faster.<br>
This repo is only the Python side. If the bug is in goome itself (drawing, a backend, the ui kit) it goes to <a href="https://github.com/goome-ui/c-goome">c-goome</a> instead, docs fixes go to <a href="https://github.com/goome-ui/docs">goome-ui/docs</a> (thats <a href="https://goome-ui.github.io/docs/">goome-ui.github.io/docs</a>) and new example projects to <a href="https://github.com/goome-ui/examples">goome-ui/examples</a>.
</p>

<details>
<summary align="center"><b>📋 The short version 📋</b></summary>

<p align="center">
• One thing per PR. One fix or one feature, if it does two things it gets closed<br>
• Open your PR against the <b>dev</b> branch, not main<br>
• Never touch <code>native/</code>, goome.h in there is copied from c-goome<br>
• Dont touch the protected files, a bot closes the PR if you do<br>
• Test it and say how you tested it, and on which OS<br>
• CI has to pass<br>
• AI is fine, but say you used it, and you need to know what every line does
</p>
</details>

<details>
<summary align="center"><b>💬 Before you start 💬</b></summary>

<p align="center">
Small fixes can go straight to a PR.<br>
For a new feature or anything big, <a href="https://github.com/goome-ui/python-goome/issues">open an issue</a> first so we can talk about it before you spend a weekend on it.<br> <br>
Same if you want to rename something or change what a function takes or returns, people already use this so I want to talk that through first.
</p>
</details>

<details>
<summary align="center"><b>🌿 Branches 🌿</b></summary>

<p align="center">
Stuff goes dev, then beta, then main. I move it along, you only ever PR into <b>dev</b>.
</p>
</details>

<details>
<summary align="center"><b>🚫 What gets closed automatically 🚫</b></summary>

<p align="center">
A bot checks every PR and closes it with a comment if it hits any of these, fix it and open a new one.<br> <br>
It has to be against <b>dev</b>, main and beta only get stuff that already sat on dev for a while.<br> <br>
It cant touch <code>.github/</code>, since thats CI and these rules and a PR could just turn them off for itself. <code>native/</code> is off limits too, <code>goome.h</code> in there gets copied from c-goome by <code>tools/update_native.sh</code> and built on everyones computer when they install. Same for <code>setup.py</code>, <code>pyproject.toml</code>, <code>MANIFEST.in</code>, <code>build.sh</code> and <code>tools/</code>, they all run on peoples computers. The <code>LICENSE</code>, the logo and the demo gif / screenshot in <code>docs/</code> stay mine to change.<br> <br>
• <b>More than 3000 changed files</b> - way too big to check<br> <br>
Renaming or moving any of those files counts too. Think one of them is wrong? <a href="https://github.com/goome-ui/python-goome/issues">Open an issue</a> and I'll fix it.
</p>
</details>

<details>
<summary align="center"><b>🤖 Using AI 🤖</b></summary>

<p align="center">
Using AI to help write your PR is allowed, as long as you say so in the PR and you know what your code does. If you get asked about something you should be able to answer without going back to the AI.<br> <br>
And test it yourself. Untested AI dumps get closed
</p>
</details>

<details>
<summary align="center"><b>🧪 Testing 🧪</b></summary>

<p align="center">
Build the library and run the tests. They all run on goome's test backend, so nothing shows up on your screen:
</p>

```sh
./build.sh test

# or by hand
./build.sh
python -m unittest -v
```

<p align="center">
On Windows run <code>./build.sh</code> from git bash with mingw gcc on your PATH. <code>CC</code> picks another compiler.<br> <br>
<code>tests/test_layout.py</code> compiles <code>tests/layout.c</code> and checks every struct in <code>goome/_lib.py</code> against what C says, plus every constant and function in goome.h, so it needs a C compiler. Without one it skips, set <code>GOOME_STRICT=1</code> to make that a fail like CI does.<br> <br>
The drawing and ui tests check the same pixel hashes as the <code>tests/unit.c</code> in c-goome, and <code>tests/test_offscreen.py</code> builds <code>tests/frame.c</code> and checks an offscreen frame hashes the same from C and from Python. Those come from the C code, so if one moves something in the bindings is passing the wrong thing. Dont just update the number.<br> <br>
<code>examples/pygame_embed.py</code> only gets tested when pygame is installed, if you touch it run it with <code>pip install pygame</code> first.<br> <br>
In the PR write a few lines on what you ran and on which OS and Python version. If it changes something you can see (an example, how something draws) add a before and after screenshot.<br> <br>
CI runs on linux (plus Python 3.8), windows and both macs when you open the PR. It has to be green before I merge.
</p>
</details>

<details>
<summary align="center"><b>✏️ Code style ✏️</b></summary>

<p align="center">
• Python 3.8 and up, so no syntax or stdlib stuff thats newer than that (no <code>match</code>, no <code>list[int]</code>, no <code>X | None</code>)<br>
• No dependencies. Only the standard library and ctypes. numpy can work with the buffers and <code>.numpy()</code> imports it when you call it, but the package never needs it. pygame only shows up in its example<br>
• No cffi or compiled extension modules, users should never need a build step besides the library itself<br>
• Every function in goome.h stays reachable. New C functions get added to <code>PROTOS</code> in <code>goome/_lib.py</code>, new struct fields to the struct there and to <code>tests/layout.c</code><br>
• Anything that holds native memory gets a <code>close()</code> and works with <code>with</code>, and closing twice is fine<br>
• Anything with a begin and an end in C works with <code>with</code> and calls the end exactly when <a href="https://goome-ui.github.io/docs/ui-app/">the docs</a> say C wants it<br>
• Match the code around it. snake_case, short names are fine inside functions<br>
• No comments unless something really isnt obvious<br>
• Dont reformat whole files, it makes the diff impossible to read
</p>
</details>

<p align="center">
Found a security hole? Dont open a public issue or PR for it, read <a href="https://github.com/goome-ui/.github/blob/main/SECURITY.md">SECURITY.md</a> and tell me privately first.<br> <br>
By sending a PR you agree your code goes out under the same <a href="LICENSE">GPL-3.0 license</a> as the rest of python-goome.
</p>
