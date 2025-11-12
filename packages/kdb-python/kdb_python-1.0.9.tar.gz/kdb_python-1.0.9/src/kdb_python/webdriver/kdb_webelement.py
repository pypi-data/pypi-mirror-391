from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement as WebDriverElement


class KDBWebElement:

    def __init__(self, web_element: WebDriverElement):
        self._web_element = web_element

    def __repr__(self):
        return self._web_element.__repr__()

    @property
    def tag_name(self):
        """This element's ``tagName`` property."""
        return self._web_element.tag_name

    @property
    def text(self):
        """The text of the element."""
        return self._web_element.text

    def click(self):
        """Clicks the element."""
        self._web_element.click()

    def submit(self):
        """Submits a form."""
        self._web_element.submit()

    def clear(self):
        """Clears the text if it's a text entry element."""
        self._web_element.clear()

    def get_property(self, name):
        """
        Gets the given property of the element.

        :Args:
            - name - Name of the property to retrieve.

        Example::

            text_length = target_element.get_property("text_length")
        """
        return self._web_element.get_property(name)

    def get_attribute(self, name):
        """Gets the given attribute or property of the element.

        This method will first try to return the value of a property with the
        given name. If a property with that name doesn't exist, it returns the
        value of the attribute with the same name. If there's no attribute with
        that name, ``None`` is returned.

        Values which are considered truthy, that is equals "true" or "false",
        are returned as booleans.  All other non-``None`` values are returned
        as strings.  For attributes or properties which do not exist, ``None``
        is returned.

        :Args:
            - name - Name of the attribute/property to retrieve.

        Example::

            # Check if the "active" CSS class is applied to an element.
            is_active = "active" in target_element.get_attribute("class")

        """

        return self._web_element.get_attribute(name)

    def is_selected(self):
        """Returns whether the element is selected.

        Can be used to check if a checkbox or radio button is selected.
        """
        return self._web_element.is_selected()

    def is_enabled(self):
        """Returns whether the element is enabled."""
        return self._web_element.is_enabled()

    def send_keys(self, *value):
        """Simulates typing into the element.

        :Args:
            - value - A string for typing, or setting form fields.  For setting
              file inputs, this could be a local file path.

        Use this to send simple key events or to fill out form fields::

            form_textfield = driver.find_element_by_name('username')
            form_textfield.send_keys("admin")

        This can also be used to set file inputs.

        ::

            file_input = driver.find_element_by_name('profilePic')
            file_input.send_keys("path/to/profilepic.gif")
            # Generally it's better to wrap the file path in one of the methods
            # in os.path to return the actual path to support cross OS testing.
            # file_input.send_keys(os.path.abspath("path/to/profilepic.gif"))

        """
        # transfer file to another machine only if remote driver is used
        # the same behaviour as for java binding
        self._web_element.send_keys(value)

    # RenderedWebElement Items
    def is_displayed(self):
        """Whether the element is visible to a user."""
        return self._web_element.is_displayed()

    @property
    def location_once_scrolled_into_view(self):
        """THIS PROPERTY MAY CHANGE WITHOUT WARNING. Use this to discover
        where on the screen an element is so that we can click it. This method
        should cause the element to be scrolled into view.

        Returns the top lefthand corner location on the screen, or ``None`` if
        the element is not visible.

        """
        return self._web_element.location_once_scrolled_into_view

    @property
    def size(self):
        """The size of the element."""
        return self._web_element.size

    def value_of_css_property(self, property_name):
        """The value of a CSS property."""
        return self._web_element.value_of_css_property(property_name)

    @property
    def location(self):
        """The location of the element in the renderable canvas."""
        return self._web_element.location

    @property
    def rect(self):
        """A dictionary with the size and location of the element."""
        return self._web_element.rect

    @property
    def screenshot_as_base64(self):
        """
        Gets the screenshot of the current element as a base64 encoded string.

        :Usage:
            img_b64 = element.screenshot_as_base64
        """
        return self._web_element.screenshot_as_base64

    @property
    def screenshot_as_png(self):
        """
        Gets the screenshot of the current element as a binary data.

        :Usage:
            element_png = element.screenshot_as_png
        """
        return self._web_element.screenshot_as_png

    def screenshot(self, filename):
        """
        Saves a screenshot of the current element to a PNG image file. Returns
           False if there is any IOError, else returns True. Use full paths in
           your filename.

        :Args:
         - filename: The full path you wish to save your screenshot to. This
           should end with a `.png` extension.

        :Usage:
            element.screenshot('/Screenshots/foo.png')
        """
        return self._web_element.screenshot(filename)

    @property
    def parent(self):
        """Internal reference to the WebDriver instance this element was found from."""
        return self._web_element.parent

    @property
    def id(self):
        """Internal ID used by selenium.

        This is mainly for internal use. Simple use cases such as checking if 2
        webelements refer to the same element, can be done using ``==``::

            if element1 == element2:
                print("These 2 are equal")

        """
        return self._web_element.id

    def __eq__(self, element):
        return self._web_element.__eq__(element)

    def __ne__(self, element):
        return self._web_element.__eq__(element)

    def find_element(self, by=By.ID, value=None):
        """
        Find an element given a By strategy and locator. Prefer the find_element_by_* methods when
        possible.

        :Usage:
            element = element.find_element(By.ID, 'foo')

        :rtype: KDBWebElement
        """
        return self._web_element.find_element(by, value)

    def find_elements(self, by=By.ID, value=None):
        """
        Find elements given a By strategy and locator. Prefer the find_elements_by_* methods when
        possible.

        :Usage:
            element = element.find_elements(By.CLASS_NAME, 'foo')

        :rtype: list of KDBWebElement
        """
        return self._web_element.find_elements(by, value)

    def __hash__(self):
        return self._web_element.__hash__()
