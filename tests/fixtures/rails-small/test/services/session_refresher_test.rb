require "test_helper"

class SessionRefresherTest < ActiveSupport::TestCase
  test "refreshes an expired session" do
    assert SessionRefresher.call("token")[:refreshed]
  end
end
