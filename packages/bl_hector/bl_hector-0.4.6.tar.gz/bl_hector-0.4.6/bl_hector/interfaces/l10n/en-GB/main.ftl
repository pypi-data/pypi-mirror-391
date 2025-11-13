# Hector --- A collection manager.
# Copyright © 2023, 2024 Bioneland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

hector = Hector

menu-books = Books
menu-login = Log in
menu-logout = Log out

# version (string) The version of the software.
# years (string) The years the copyright applies to.
# holders (string) The names of the copyright holders.
copyright = Version { $version } © { $years } { $holders }.

# name (string) The name of the license.
# url (string) The URL of the license file.
license = Code is licensed under <a href="{ $url }">{ $name }</a>.

# name (string) The name of the information to display
# value (string) The value of the information to display
info-line = { $name }: { $value }

access-forbidden = Access forbidden!
access-not-authorized = Access unauthorised!
an-error-occurred = An error occurred!
bad-request = You submitted a bad request! This should have never happened!?

# date (Date) A date to format
date = { $date }

book = book
books = books
book-added-on = added on
book-updated-on = update on
book-isbn = ISBN
book-isbn-description = The ISBN assigned to the book, for instance 978-0-7653-9277-0.
book-title = title
book-title-description = The title of the book.
book-year = year
book-year-description = The year the book was published in.
book-author = author
book-author-description = One of the authors of the book.
book-authors = authors
book-authors-description = The list of authors of the book, comma separated.
book-genre = genre
book-genre-description = One of the genres the book belongs to.
book-genres = genres
book-genres-description = The list of genres the book belongs to, comma separated.

unknown-error = An unknown error has occurred!
mandatory-value = This value is mandatory!
incorrect-value = Incorrect value!
# min (int) The minimum length
string-too-short = The minimal length is { $min }.
# max (int) The maximum length
string-too-long = The maximal length is { $max }.
# min (float) The minimum value
number-too-small = The minimal value is { $min }.
# max (float) The maximum value
number-too-big = The maximal value is { $max }.
unknown-book = Unknown book
not-an-isbn = This is not an ISBN!
missing-author = A book must have an author.
# year (string) The year of creation
before-creation-of-isbn = ISBN system was introduced in { $year }.

auth-login-title = Log in
# method (string) The sign in method
auth-login-method = Sign in using { $method }
auth-logged-out = You’ve been successfully logged out.

webauthn-register-title = Device registration
webauthn-register-description = Your browser should be asking you to tap your security device…
webauthn-register-success = Your security device has been succesfully registered!
webauthn-register-failure = Your security device could not be registered!?

webauthn-login-title = Log in
webauthn-login-description = Your browser should be asking you to tap your security device…
webauthn-login-failure = You couldn't be logged in!?

totp-login-title = Log in
totp-login-description = Please enter your one-time password.
totp-login-password = Password
totp-login-pattern = An TOTP code is made up of 6 digits.
totp-login-action = Log in
totp-login-error = Error authenticating with TOTP.
totp-login-success = Success authenticating with TOTP.

ip-login-error = Error authenticating with IP.
ip-login-success = Success authenticating with IP.

add-book-requires-authentification = You must be authenticated before adding a book!
add-book-title = Add a new book to the collection
add-book-action = Add a book
add-book-cancel = Cancel
add-book-add = Add
add-book-cover-help = Click to upload a cover
add-book-cover-format-not-supported = The format of this cover is not supported!

search-books-title = Search for a book
search-books-action = Look up book
search-books-clear = Clear
search-books-search = Search
search-books-no-result = No matching book!
search-books-previous-page = Previous
search-books-next-page = Next

# title (string) The title of the book
display-book-title = Details for "{ $title }"

update-book-requires-authentification = You must be authenticated before editing a book!
# isbn (string) The ISBN of the book
update-book-title = Edit information for `{ $isbn }`
update-book-action = Edit
update-book-failure = Book cannot be updated!
update-book-success = Book has been updated!
update-book-cancel = Cancel
update-book-update = Save
update-book-cover-help = Click to upload a new cover
update-book-cover-format-not-supported = The format of this cover is not supported!

book-does-not-exist = The book you are looking for is not in the collection!
book-already-exists = Book already in the collection!
# isbn (string) The ISBN of the book
# url (string) The URL of the book
book-added-html = Book <a href="{ $url }">{ $isbn }</a> successfully added!
# isbn (string) The ISBN of the book
book-added-text = Book { $isbn } successfully added!
book-added = Book <a href="{ $url }">{ $isbn }</a> successfully added!
book-not-found = Book not found!
book-cannot-be-added = The book cannot be added!
books-cannot-be-found = The search cannot be performed!
