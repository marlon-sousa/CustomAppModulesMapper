# -*- coding: UTF-8 -*-
# A part of the CustomAppModulesMapper addon for NVDA
# Copyright (C) 2024 Marlon Sousa
# This file is covered by the MIT License.
# See the file COPYING.txt for more details.

import appModuleHandler


# A deliberately empty app module. Mapping an application to "notAssociated" gives it a neutral
# app module that adds no app specific behavior, which effectively detaches the application from
# whatever module NVDA would otherwise load for it.
class AppModule(appModuleHandler.AppModule):
	pass
