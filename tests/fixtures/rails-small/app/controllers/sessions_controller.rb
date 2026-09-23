class SessionsController < ApplicationController
  def refresh
    render json: SessionRefresher.call(params[:refresh_token])
  end
end
