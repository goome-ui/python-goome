import unittest

import goome


class Ax(object):
    def __init__(self):
        self.g = goome.Goome(backend=goome.TEST, mode=goome.MODE_WINDOW, width=420, height=700, test_script="end 100000")
        self.u = self.g.ui()
        self.u.theme.font = None
        self.ok = self.custom_hits = 0
        self.dark, self.mode, self.fruit, self.tab, self.vol = False, 0, 0, 0, 2.0
        self.open = goome.Flag(False)
        self.name, self.note = "Bo", ""
        self.nodes = []

    def frame(self):
        u = self.u
        for ev in self.g.events(0):
            u.feed(ev)
        if u.begin(0) is None:
            return
        with u.app("Demo", goome.APP_TITLEBAR | goome.APP_STATUSBAR):
            u.label("Hello there")
            if u.button("OK"):
                self.ok += 1
            self.dark = u.checkbox("Dark", self.dark)
            self.mode = u.radio("Big", self.mode, 1)
            self.vol = u.slider("Volume", self.vol, 0, 10, "%.1f")
            self.name = u.input("Name", self.name, 64)
            self.fruit = u.combo("Fruit", self.fruit, ["Mango", "Kiwi", "Fig"])
            self.tab = u.tabs("tabs", ["One", "Two"], self.tab)
            with u.tree("Folder", self.open) as shown:
                if shown:
                    u.label("inside")
            u.progress(0.25)
            self.note = u.text_edit("Notes", self.note, 60, 0, 256)
            u.a11y_role("button", "Knob")
            u.a11y_value("11")
            if u.custom("knob", 40, 40).clicked:
                self.custom_hits += 1
            u.statusbar("ready")
        u.end()
        self.nodes = u.a11y_tree()

    def find(self, role, label):
        for n in self.nodes:
            if n.role == role and n.label == label:
                return n
        return None

    def close(self):
        self.u.close()
        self.g.close()


class A11y(unittest.TestCase):
    def test_tree_and_actions(self):
        R = goome
        k = Ax()
        try:
            k.frame()
            n = k.nodes
            self.assertGreater(len(n), 15)
            app, ok, dark = k.find(R.ROLE_WINDOW, "Demo"), k.find(R.ROLE_BUTTON, "OK"), k.find(R.ROLE_CHECKBOX, "Dark")
            vol, name, fruit = k.find(R.ROLE_SLIDER, "Volume"), k.find(R.ROLE_INPUT, "Name"), k.find(R.ROLE_COMBO, "Fruit")
            tree, knob, tab2 = k.find(R.ROLE_TREE, "Folder"), k.find(R.ROLE_BUTTON, "Knob"), k.find(R.ROLE_TAB, "Two")
            big, notes = k.find(R.ROLE_RADIO, "Big"), k.find(R.ROLE_INPUT, "Notes")
            self.assertTrue(app.index == 0 and app.parent == -1 and app.role_name == "window")
            self.assertTrue(ok.parent == app.index and ok.w > 0 and ok.h > 0)
            self.assertIsNotNone(k.find(R.ROLE_TEXT, "Hello there"))
            self.assertIsNotNone(k.find(R.ROLE_TEXT, "ready"))
            self.assertIsNotNone(k.find(R.ROLE_BUTTON, "Close"))
            self.assertIsNotNone(k.find(R.ROLE_BUTTON, "Minimize"))
            self.assertFalse(dark.checked or big.checked)
            self.assertEqual((vol.num, vol.min, vol.max, vol.value), (2, 0, 10, "2.0"))
            self.assertEqual(name.value, "Bo")
            self.assertTrue(fruit.value == "Mango" and not fruit.expanded)
            self.assertTrue(n[tab2.parent].role == R.ROLE_GROUP and not tab2.selected)
            self.assertTrue(k.find(R.ROLE_TAB, "One").selected)
            self.assertTrue(not tree.expanded and k.find(R.ROLE_TEXT, "inside") is None)
            self.assertEqual(knob.value, "11")
            self.assertIsNotNone(notes)
            pr = [x for x in n if x.role == R.ROLE_PROGRESS]
            self.assertTrue(pr and pr[0].num == 0.25 and pr[0].value == "25%")
            ids = [x.id for x in n]
            k.frame()
            self.assertEqual([x.id for x in k.nodes], ids)
            self.assertEqual(len(set(ids)), len(ids))

            u = k.u
            u.a11y_action("press", ok)
            u.a11y_action("press", dark)
            u.a11y_action("press", big)
            u.a11y_action("set", vol, "7.5")
            u.a11y_action("set", name, "hello there")
            u.a11y_action("press", knob)
            u.a11y_action("expand", tree)
            u.a11y_action("press", tab2.id)
            u.a11y_action("set", notes, "line one")
            k.frame()
            self.assertEqual((k.ok, k.dark, k.mode, k.vol, k.name, k.custom_hits, k.open.value, k.tab), (1, True, 1, 7.5, "hello there", 1, True, 1))
            self.assertEqual(k.note, "line one")
            k.frame()
            self.assertTrue(k.find(R.ROLE_CHECKBOX, "Dark").checked)
            self.assertEqual(k.find(R.ROLE_SLIDER, "Volume").value, "7.5")
            self.assertEqual(k.find(R.ROLE_INPUT, "Name").value, "hello there")
            tree = k.find(R.ROLE_TREE, "Folder")
            self.assertTrue(tree.expanded and k.find(R.ROLE_TEXT, "inside").parent == tree.index)

            u.a11y_action("focus", k.find(R.ROLE_INPUT, "Name"))
            k.frame()
            k.frame()
            name = k.find(R.ROLE_INPUT, "Name")
            self.assertTrue(name.focused and name.caret == 11)
            self.assertEqual(sum(x.focused for x in k.nodes), 1)

            u.a11y_action("expand", k.find(R.ROLE_COMBO, "Fruit"))
            k.frame()
            k.frame()
            fruit, fig = k.find(R.ROLE_COMBO, "Fruit"), k.find(R.ROLE_ITEM, "Fig")
            self.assertTrue(fruit.expanded and fig is not None)
            self.assertTrue(k.nodes[fig.parent].role == R.ROLE_LIST and k.nodes[fig.parent].parent == fruit.index)
            u.a11y_action("press", fig)
            k.frame()
            k.frame()
            self.assertTrue(k.fruit == 2 and k.find(R.ROLE_ITEM, "Fig") is None)
            self.assertEqual(k.find(R.ROLE_COMBO, "Fruit").value, "Fig")
            u.a11y_action("set", k.find(R.ROLE_COMBO, "Fruit"), "Kiwi")
            k.frame()
            self.assertEqual(k.fruit, 1)
            with self.assertRaises(ValueError):
                u.a11y_action("poke", 1)

            u.a11y(False)
            k.frame()
            self.assertEqual(k.nodes, [])
        finally:
            k.close()

    def test_offscreen_off_by_default(self):
        with goome.open_offscreen(200, 100) as g, g.ui() as u:
            u.theme.font = None
            for want in (0, 1):
                with u.frame(0):
                    u.button("Hi")
                self.assertEqual(len(u.a11y_tree()), want)
                u.a11y(True)
            with u.frame(0):
                u.button("Hi")
            n = u.a11y_tree()
            self.assertEqual([(x.role, x.label, x.role_name) for x in n], [(goome.ROLE_BUTTON, "Hi", "button")])
            self.assertIn("button 'Hi'", repr(n[0]))


if __name__ == "__main__":
    unittest.main()
