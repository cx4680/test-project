package handler

import (
	"my-test/internal/model"
	"my-test/internal/service"
	"net/http"

	"github.com/gin-gonic/gin"
)

func Hello(c *gin.Context) {
	msg := service.Hello()
	c.JSON(http.StatusOK, model.Response{
		Code:    0,
		Message: msg,
		Data:    nil,
	})
}
