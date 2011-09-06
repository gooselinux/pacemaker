%global gname haclient
%global uname hacluster
%global pcmk_docdir %{_docdir}/%{name}

# Supported cluster stacks, must support at least one
%bcond_without ais
%bcond_without cman
%bcond_with heartbeat

# ESMTP is not available in RHEL, only in EPEL. Allow people to build
# the RPM without ESMTP in case they choose not to use EPEL packages
%bcond_without esmtp

# SNMP trap support only works with Net-SNMP 5.4 and above
%bcond_without snmp

# We generate some docs using Publican, but its not available everywhere
%bcond_without publican

%global specversion 7
%global upstream_version Pacemaker-1.1.2.1
%global upstream_prefix Pacemaker-1-1-

# Keep around for when/if required
#global alphatag %{upstream_version}.hg

%global pcmk_release %{?alphatag:0.}%{specversion}%{?alphatag:.%{alphatag}}%{?dist}

# Compatibility macros for distros that don't provide Python macros by default.
# Do this instead of trying to conditionally include
# %{_rpmconfigdir}/macros.python which doesn't always exist
%{!?py_ver:	%{expand: %%global py_ver      %%(echo `python -c "import sys; print sys.version[:3]"`)}}
%{!?py_prefix:	%{expand: %%global py_prefix   %%(echo `python -c "import sys; print sys.prefix"`)}}
%{!?py_libdir:	%{expand: %%global py_libdir  %%{expand:%%%%{py_prefix}/%%%%{_lib}/python%%%%{py_ver}}}}
%{!?py_sitedir:	%{expand: %%global py_sitedir %%{expand:%%%%{py_libdir}/site-packages}}}

# When downloading directly from Mercurial, it will automatically add a prefix
# Invoking 'hg archive' wont but you can add one with:
# hg archive -t tgz -p "$upstream_prefix-$upstream_version" -r $upstream_version $upstream_version.tar.gz

Name:		pacemaker
Summary:	Scalable High-Availability cluster resource manager
Version:	1.1.2
Release:	%{pcmk_release}
License:	GPLv2+ and LGPLv2+
Url:		http://www.clusterlabs.org
Group:		System Environment/Daemons
Source0:	http://hg.clusterlabs.org/pacemaker/1.1/archive/%{upstream_version}.tar.bz2
Patch1:		cman-mcp-support.patch
Patch2:		cib-no-forked-writes.patch
Patch3:		pcmk-service-id.patch
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
AutoReqProv:	on
Requires(pre):	cluster-glue
Requires:	resource-agents
Requires:	perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:	pacemaker-libs = %{version}-%{release}

ExclusiveArch: i686 x86_64

# Required for core functionality
BuildRequires:	automake autoconf libtool pkgconfig libtool-ltdl-devel python-devel
BuildRequires:	glib2-devel cluster-glue-libs-devel libxml2-devel libxslt-devel 
BuildRequires:	pkgconfig python-devel gcc-c++ bzip2-devel gnutls-devel pam-devel

# Enables optional functionality
BuildRequires:	help2man ncurses-devel openssl-devel libselinux-devel resource-agents

%if %{with esmtp}
BuildRequires:	libesmtp-devel
%endif

%if %{with snmp}
BuildRequires:	net-snmp-devel >= 5.4
Requires:	net-snmp >= 5.4
%endif

%if %{with cman}
BuildRequires:	clusterlib-devel
%endif

%if %{with ais}
BuildRequires:	corosynclib-devel
Requires:	corosync
%endif

%if %{with heartbeat}
BuildRequires:	heartbeat-devel heartbeat-libs
Requires:	heartbeat >= 3.0.0
%endif

%if %{with publican}
BuildRequires:	publican
%endif

%description
Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%package -n pacemaker-libs
License:	GPLv2+ and LGPLv2+
Summary:	Libraries used by the Pacemaker cluster resource manager and its clients
Group:		System Environment/Daemons

%description -n pacemaker-libs
Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%package -n pacemaker-libs-devel 
License:	GPLv2+ and LGPLv2+
Summary:	Pacemaker development package
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	cluster-glue-libs-devel
%if %{with ais}
Requires:	corosynclib-devel
%endif
%if %{with heartbeat}
Requires:	heartbeat-devel
%endif

%description -n pacemaker-libs-devel
Headers and shared libraries for developing tools for Pacemaker.

Pacemaker is an advanced, scalable High-Availability cluster resource
manager for Linux-HA (Heartbeat) and/or OpenAIS.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%package	cts
License:	GPLv2+ and LGPLv2+
Summary:	Test framework for cluster-related technologies like Pacemaker
Group:		System Environment/Daemons
Requires:	python

%description	cts
Test framework for cluster-related technologies like Pacemaker

%package	doc
License:	GPLv2+ and LGPLv2+
Summary:	Documentation for Pacemaker
Group:		Documentation

%description	doc
Documentation for Pacemaker.

Pacemaker is an advanced, scalable High-Availability cluster resource
manager for OpenAIS/Corosync.

It supports "n-node" clusters with significant capabilities for
managing resources and dependencies.

It will run scripts at initialization, when machines go up or down,
when related resources fail and can be configured to periodically check
resource health.

%prep
%setup -q -n %{upstream_prefix}%{upstream_version}
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
./autogen.sh
%{configure}				\
	%{?_without_heartbeat}		\
	%{?_without_cman}		\
	%{?_without_ais}		\
	%{?_without_esmtp}		\
	%{?_without_snmp}		\
	--with-initdir=%{_initddir}	\
	--docdir=%{pcmk_docdir}		\
	--localstatedir=%{_var}		\
	--enable-fatal-warnings=no

make %{_smp_mflags}

%install
rm -rf %{buildroot}
make DESTDIR=%{buildroot} install

# Scripts that need to be executable
chmod a+x %{buildroot}/%{_datadir}/pacemaker/tests/cts/CTSlab.py
chmod a+x %{buildroot}/%{_datadir}/pacemaker/tests/cts/extracttests.py

# These are not actually scripts
find %{buildroot} -name '*.xml' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.xsl' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.rng' -type f -print0 | xargs -0 chmod a-x
find %{buildroot} -name '*.dtd' -type f -print0 | xargs -0 chmod a-x
 
# Dont package static libs or compiled python
find %{buildroot} -name '*.a' -type f -print0 | xargs -0 rm -f
find %{buildroot} -name '*.la' -type f -print0 | xargs -0 rm -f

# Remove legacy wrappers and their man pages
rm -f %{buildroot}/%{_sbindir}/fence_legacy
rm -f %{buildroot}/%{_mandir}/man8/fence_legacy.8*

rm -f %{buildroot}/%{_sbindir}/crm_standby
rm -f %{buildroot}/%{_mandir}/man8/crm_standby.8*

rm -f %{buildroot}/%{_sbindir}/crm_failcount
rm -f %{buildroot}/%{_mandir}/man8/crm_failcount.8*

rm -f %{buildroot}/%{_libdir}/heartbeat/hb2openais-helper.py*
rm -f %{buildroot}/%{_libdir}/heartbeat/crm_primitive.py*

# Don't package these either
rm -rf %{buildroot}/%{_var}/run/crm
rm -f %{buildroot}/%{_sbindir}/cibpipe
rm -f %{buildroot}/%{_libdir}/service_crm.so
rm -f %{buildroot}/usr/lib/ocf/resource.d/pacemaker/pingd

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add pacemaker || :

%preun
if [ $1 -eq 0 ]; then
    /sbin/service pacemaker stop &>/dev/null || :
    /sbin/chkconfig --del pacemaker || :
fi

%post -n pacemaker-libs -p /sbin/ldconfig

%postun -n pacemaker-libs -p /sbin/ldconfig

%files
###########################################################
%defattr(-,root,root)

%exclude %{_datadir}/pacemaker/tests

%{_initddir}/pacemaker
%{_datadir}/pacemaker
%{_datadir}/snmp/mibs/PCMK-MIB.txt
%{_libdir}/heartbeat/*
%{_sbindir}/cibadmin
%{_sbindir}/crm
%{_sbindir}/crm_attribute
%{_sbindir}/crm_diff
%{_sbindir}/crm_mon
%{_sbindir}/crm_master
%{_sbindir}/crm_simulate
%{_sbindir}/crm_resource
%{_sbindir}/crm_report
%{_sbindir}/crm_verify
%{_sbindir}/crmadmin
%{_sbindir}/iso8601
%{_sbindir}/attrd_updater
%{_sbindir}/ptest
%{_sbindir}/pacemakerd
%{_sbindir}/crm_shadow
%{_sbindir}/crm_node
%{_sbindir}/stonith_admin
%{py_sitedir}/crm
%{_mandir}/man8/*.8*
%{_mandir}/man7/*.7*

%if %{with heartbeat}
%{_sbindir}/crm_uuid
%else
%exclude %{_sbindir}/crm_uuid
%endif

# Packaged elsewhere
%exclude %{_datadir}/pacemaker/tests

%doc COPYING
%doc AUTHORS

%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/heartbeat/crm
%dir %attr (750, %{uname}, %{gname}) %{_var}/lib/pengine
%dir /usr/lib/ocf
%dir /usr/lib/ocf/resource.d
/usr/lib/ocf/resource.d/pacemaker
%if %{with ais}
%{_libexecdir}/lcrso/pacemaker.lcrso
%endif

%files -n pacemaker-libs
%defattr(-,root,root)
%{_libdir}/libcib.so.*
%{_libdir}/libcrmcommon.so.*
%{_libdir}/libcrmcluster.so.*
%{_libdir}/libpe_status.so.*
%{_libdir}/libpe_rules.so.*
%{_libdir}/libpengine.so.*
%{_libdir}/libtransitioner.so.*
%{_libdir}/libstonithd.so.*
%doc COPYING.LIB
%doc AUTHORS

%files doc
%defattr(-,root,root)
%doc %{pcmk_docdir}

%files cts
%defattr(-,root,root)
%{py_sitedir}/cts
%{_datadir}/pacemaker/tests/cts
%doc COPYING.LIB
%doc AUTHORS

%files -n pacemaker-libs-devel
%defattr(-,root,root)
%exclude %{_datadir}/pacemaker/tests/cts
%{_datadir}/pacemaker/tests
%{_includedir}/pacemaker
%{_libdir}/*.so
%doc COPYING.LIB
%doc AUTHORS

%changelog
* Tue Jul 13 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-7
- Resolves: rhbz#610815 - add cman support
  + High: ais: Use service slot 10 to avoid conflicting with cman

* Sat Jul 10 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-6
- Resolves: rhbz#610815 - add cman support
  + High: cib: Also free query result for xpath operations that return more than one hit
  + High: cib: Fix the application of unversioned diffs
  + High: Core: Correctly unpack HA_Messages containing multiple entries with the same name
  + High: Core: Resolve coverity RESOURCE_LEAK defects
  + High: crmd: All nodes should see status updates, not just he DC
  + High: crmd: Allow non-DC nodes to clear failcounts too
  + High: crmd: Base DC election on process relative uptime
  + High: crmd: Make sure the membership cache is accurate after a sucessful fencing operation
  + High: crmd: Make sure we always poke the FSA after a transition to clear any TE_HALT actions
  + High: crmd: Prevent segmentation fault
  + High: PE: Avoid creating invalid ordering constraints for probes that are not needed
  + High: PE: Bug lf#1959 - Fail unmanaged resources should not prevent other services from shutting down
  + High: PE: Bug lf#2422 - Ordering dependencies on partially active groups not observed properly
  + High: PE: Bug lf#2424 - Use notify oepration definition if it exists in the configuration
  + High: PE: Bug lf#2433 - No services should be stopped until probes finish
  + High: PE: Correctly detect when there is a real failcount that expired and needs to be cleared
  + High: PE: Correctly handle pseudo action creation
  + High: PE: Fix colocation for interleaved clones
  + High: PE: Fix colocation with partially active groups
  + High: PE: Fix potential use-after-free defect from coverity
  + High: PE: Fix use-after-free in order_actions() reported by valgrind
  + High: PE: Prevent endless loop when looking for operation definitions in the configuration
  + High: stonith: Correctly parse pcmk_host_list parameters that appear on a single line
  + High: tools: crm_simulate - Resolve coverity USE_AFTER_FREE defect

* Tue May 25 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-5
- Resolves: rhbz#594296 - rpmdiff checks
  + Remove legacy scripts
  + Add missing man pages
  + Fix sub-package version requires

* Tue May 18 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-3
- Resolves: rhbz#590667
- Rebase on new upstream release
  + High: Core: Bug lf#2401 - Backed out changeset 6e6980376f01

* Wed May 12 2010 Andrew Beekhof <andrew@beekhof.net> 1.1.2-2
- Do not build on ppc and ppc64.
  Resolves: rhbz#590992
- Rebase on new upstream release
  + High: ais: Do not count votes from offline nodes and calculate current votes before sending quorum data
  + High: ais: Ensure the list of active processes sent to clients is always up-to-date
  + High: ais: Look for the correct conf variable for turning on file logging
  + High: ais: Use the threadsafe version of getpwnam
  + High: Core: Bug lf#2414 - Prevent use-after-free reported by valgrind when doing xpath based deletions
  + High: Core: fix memory leaks exposed by valgrind
  + High: crmd: Bug 2401 - Improved detection of partially active peers
  + High: crmd: Bug lf#2379 - Ensure the cluster terminates when the PE is not available
  + High: crmd: Bug lf#2414 - Prevent use-after-free of the PE connection after it dies
  + High: crmd: Bug lf#2414 - Prevent use-after-free of the stonith-ng connection
  + High: crmd: Do not allow the target_rc to be misused by resource agents
  + High: crmd: Do not ignore action timeouts based on FSA state
  + High: crmd: Ensure we dont get stuck in S_PENDING if we loose an election to someone that never talks to us again
  + High: crmd: Fix memory leaks exposed by valgrind
  + High: crmd: Remove race condition that could lead to multiple instances of a clone being active on a machine
  + High: crmd: Send erase_status_tag() calls to the local CIB when the DC is fenced, since there is no DC to accept them
  + High: crmd: Use global fencing notifications to prevent secondary fencing operations of the DC
  + High: PE: Bug lf#2317 - Avoid needless restart of primitive depending on a clone
  + High: PE: Bug lf#2361 - Ensure clones observe mandatory ordering constraints if the LHS is unrunnable
  + High: PE: Bug lf#2383 - Combine failcounts for all instances of an anonymous clone on a host
  + High: PE: Bug lf#2384 - Fix intra-set colocation and ordering
  + High: PE: Bug lf#2403 - Enforce mandatory promotion (colocation) constraints
  + High: PE: Bug lf#2412 - Correctly locate clone instances by their prefix
  + High: PE: Don ot be so quick to pull the trigger on nodes that are coming up
  + High: PE: Fix memory leaks exposed by valgrind
  + High: PE: Repair handling of unordered groups in RHS ordering constraints
  + High: PE: Rewrite native_merge_weights() to avoid Fix use-after-free
  + High: Shell: always reload status if working with the cluster (bnc#590035)
  + High: Shell: check timeouts also against the default-action-timeout property
  + High: Shell: Default to using the status section from the live CIB (bnc#592762)
  + High: Shell: edit multiple meta_attributes sets in resource management (lf#2315)
  + High: Shell: enable comments (lf#2221)
  + High: Tools: crm_mon - fix memory leaks exposed by valgrind

* Mon Mar 08 2010 Andrew Beekhof <andrew@beekhof.net> - 1.1.1-2
- Resolves: rhbz#570807 - Offline nodes should not have their quorum votes counted

* Thu Mar 04 2010 Andrew Beekhof <andrew@beekhof.net> - 1.1.1-1
- Resolves: rhbz#559868
- Split off the doc package as it has grown quite large
- Split off the cluster test suite (CTS) so that it can be used by other projects 
- Update the tarball from upstream to version 46e288ab9014
  + High: PE: Repair handling of unordered groups in RHS ordering constraints
  + High: Agents: Prevent shell expansion of '*' when there are files in /var/lib/heartbeat/cores/root
  + High: ais: Bug lf#2340 - Force rogue child processes to terminate after waiting 2.5 minutes
  + High: ais: Bug lf#2359 - Default expected votes to 2 inside Corosync/OpenAIS plugin
  + High: ais: Bug lf#2359 - expected-quorum-votes not correctly updated after membership change
  + High: ais: Bug rhbz#525552 - Move non-threadsafe calls to setenv() to after the fork()
  + High: crmd: Bug bnc#578644 - Improve handling of cancelled operations caused by resource cleanup
  + High: crmd: Make sure we wait for fencing to complete before continuing
  + High: crmd: Prevent use-of-NULL when non-DCs get stonith callbacks
  + High: Fencing: Account for stonith_get_info() always returning a pointer to the same static buffer
  + High: Fencing: Bug bnc#577007 - Correctly parse the hostlist output from stonith agents
  + High: Fencing: Correctly parse arg maps and do not return a provider for unknown agents
  + High: fencing: Fix can_fence_host_with_device() logic and improve hostlist output parsing
  + High: PE: Bug lf#2358 - Fix master-master anti-colocation
  + High: PE: Correctly implement optional colocation between primitives and clone resources
  + High: PE: Suppress duplicate ordering constraints to achieve orders of magnitude speed increases for large clusters
  + High: Shell: move scores from resource sets to the constraint element (lf#2331)
  + High: Shell: recovery from bad/outdated help index file
  + Medium: Shell: implement lifetime for rsc migrate and node standby (lf#2353)
  + Medium: Shell: node attributes update in configure (bnc#582767)

* Thu Feb 25 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 1.1.0-2
- Resolves: rhbz#568008
- Do not build pacemaker on s390 and s390x.

* Fri Jan 15 2010 Andrew Beekhof <andrew@beekhof.net> - 1.1.0-1
- Related: rhbz#543948
- Update the tarball from upstream to version 07ab245be519
  + High: crmd: Always connect to stonith
  + High: crmd: Ensure batch-limit is correctly enforced
  + High: crmd: Ensure we have the latest status after a transition abort
  + High: Fencing: Overhaul the fencing daemon
  + High: PE: Bug lf#2153 - non-clones shouldn't restart when clones stop/start on other nodes - improved
  + Medium: PE: Allow resource sets to be reused between ordering and colocation constraints
  + Medium: PE: Implement serializing order constraints that dont cause restarts or inhibit migration
  + Medium: PE: Include node attributes for the node to be fenced
  + Medium: PE: Make crm_simulate a full replacement for ptest
  + Medium: PE: Only complain about target-role=master for non m/s resources
  + Medium: PE: Prevent non-multistate resources from being promoted through target-role
  + Medium: PE: Simplify the rsc_order syntax - don't make funky inferences based on score
  + Medium: PE: Support serialized sets of resources
  + Medium: Tools: Bug lf#2286 - Allow the shell to accept template parameters on the command line
  + Medium: Tools: Bug lf#2307 - Provide a way to determin the nodeid of past cluster members
  + Medium: Tools: crm: add update method to template apply (LF 2289)
  + Medium: Tools: crm: direct RA interface for stonith class resource agents (LF 2270)
  + Medium: Tools: crm: don't remove sets which contain id-ref attribute (LF 2304)
  + Medium: Tools: crm: exclude locations when testing for pathological constraints (LF 2300)
  + Medium: Tools: crm: fix exit code on single shot commands
  + Medium: Tools: crm: fix node delete (LF 2305)
  + Medium: Tools: crm: implement -F (--force) option
  + Medium: Tools: crm: rename status to cibstatus (LF 2236)
  + Medium: Tools: crm: stay in crm if user specified level only (LF 2286)

* Tue Dec 15 2009 Andrew Beekhof <andrew@beekhof.net> - 1.1.0-0.1-00d9bcac8775.hg
- Related: rhbz#rhbz#543948
- Update the tarball from upstream to version 00d9bcac8775
  + High: PE: Bug 2213 - Ensure groups process location constraints so that clone-node-max works for cloned groups
  + High: PE: Bug lf#2153 - Update regression tests
  + High: PE: Bug lf#2153 - non-clones shouldn't restart when clones stop/start on other nodes
  + High: PE: Bug lf#2209 - Clone ordering should be able to prevent startup of dependant clones
  + High: PE: Bug lf#2216 - Correctly identify the state of anonymous clones when deciding when to probe
  + High: PE: Bug lf#2225 - Operations that require fencing should wait for 'stonith_complete' not 'all_stopped'.
  + High: PE: Bug lf#2225 - Prevent clone peers from stopping while another is instance is (potentially) being fenced
  + High: PE: Correctly anti-colocate with a group
  + High: PE: Correctly unpack ordering constraints for resource sets to avoid graph loops
  + High: Replace stonithd with the new fencing subsystem
  + High: cib: Ensure the loop searching for a remote login message terminates
  + High: cib: Finally fix reliability of receiving large messages over remote plaintext connections
  + High: cib: Fix remote notifications
  + High: cib: For remote connections, default to CRM_DAEMON_USER since thats the only one that the cib can validate the password for using PAM
  + High: cib: Remote plaintext - Retry sending parts of the message that didn't fit the first time
  + Medium: PE: Bug lf#2206 - rsc_order constraints always use score at the top level
  + Medium: PE: Provide a default action for resource-set ordering
  + Medium: PE: Silently fix requires=fencing for stonith resources so that it can be set in op_defaults
  + Medium: ais: Some clients such as gfs_controld want a cluster name, allow one to be specified in corosync.conf
  + Medium: cib: Create valid notification control messages
  + Medium: cib: Indicate where the remote connection came from
  + Medium: cib: Send password prompt to stderr so that stdout can be redirected
  + Medium: extra: Add the daemon parameter to the controld metadata
  + Medium: fencing: Re-engineer the stonith daemon to support RHCS agents
  + Medium: tools: Make crm_mon functional with remote connections
  + Medium: xml: Bug bnc#552713 - Treat node unames as text fields not IDs
  + Medium: xml: Bug lf#2215 - Create an always-true expression for empty rules when upgrading from 0.6

* Thu Dec 03 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.0.5-6.2
- Rebuilt for RHEL 6

* Wed Nov 25 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.0.5-6.1
- Rebuilt for RHEL 6

* Sat Oct 31 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-6
- Let snmp automatically pull in lm_sensors-devel if required
  and available on that arch (its not on s390x)

* Sat Oct 31 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-5
- Disable Heartbeat support

* Thu Oct 29 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-4
- Include the fixes from CoroSync integration testing
- Move the resource templates - they're not documentation
- Ensure documentation is placed in a standard location
- Exclude documentation that is included elsewhere in the package

- Update the tarball from upstream to version ee19d8e83c2a
  + High: cib: Correctly clean up when both plaintext and tls remote ports are requested
  + High: PE: Bug bnc#515172 - Provide better defaults for lt(e) and gt(e) comparisions
  + High: PE: Bug lf#2197 - Allow master instances placemaker to be influenced by colocation constraints
  + High: PE: Make sure promote/demote pseudo actions are created correctly
  + High: PE: Prevent target-role from promoting more than master-max instances
  + High: ais: Bug lf#2199 - Prevent expected-quorum-votes from being populated with garbage
  + High: ais: Prevent deadlock - dont try to release IPC message if the connection failed
  + High: cib: For validation errors, send back the full CIB so the client can display the errors
  + High: cib: Prevent use-after-free for remote plaintext connections
  + High: crmd: Bug lf#2201 - Prevent use-of-NULL when running heartbeat

* Wed Oct 13 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-3
- Update the tarball from upstream to version 38cd629e5c3c
  + High: Core: Bug lf#2169 - Allow dtd/schema validation to be disabled
  + High: PE: Bug lf#2106 - Not all anonymous clone children are restarted after configuration change
  + High: PE: Bug lf#2170 - stop-all-resources option had no effect
  + High: PE: Bug lf#2171 - Prevent groups from starting if they depend on a complex resource which can't
  + High: PE: Disable resource management if stonith-enabled=true and no stonith resources are defined
  + High: PE: Don't include master score if it would prevent allocation
  + High: ais: Avoid excessive load by checking for dead children every 1s (instead of 100ms)
  + High: ais: Bug rh#525589 - Prevent shutdown deadlocks when running on CoroSync
  + High: ais: Gracefully handle changes to the AIS nodeid
  + High: crmd: Bug bnc#527530 - Wait for the transition to complete before leaving S_TRANSITION_ENGINE
  + High: crmd: Prevent use-after-free with LOG_DEBUG_3
  + Medium: xml: Mask the "symmetrical" attribute on rsc_colocation constraints (bnc#540672)
  + Medium (bnc#520707): Tools: crm: new templates ocfs2 and clvm
  + Medium: Build: Invert the disable ais/heartbeat logic so that --without (ais|heartbeat) is available to rpmbuild
  + Medium: PE: Bug lf#2178 - Indicate unmanaged clones
  + Medium: PE: Bug lf#2180 - Include node information for all failed ops
  + Medium: PE: Bug lf#2189 - Incorrect error message when unpacking simple ordering constraint
  + Medium: PE: Correctly log resources that would like to start but can't
  + Medium: PE: Stop ptest from logging to syslog
  + Medium: ais: Include version details in plugin name
  + Medium: crmd: Requery the resource metadata after every start operation

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 1.0.5-2.1
- rebuilt with new openssl

* Wed Aug 19 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-2
- Add versioned perl dependancy as specified by
    https://fedoraproject.org/wiki/Packaging/Perl#Packages_that_link_to_libperl
- No longer remove RPATH data, it prevents us finding libperl.so and no other
  libraries were being hardcoded
- Compile in support for heartbeat
- Conditionally add heartbeat-devel and corosynclib-devel to the -devel requirements 
  depending on which stacks are supported

* Mon Aug 17 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-1
- Add dependancy on resource-agents
- Use the version of the configure macro that supplies --prefix, --libdir, etc
- Update the tarball from upstream to version 462f1569a437 (Pacemaker 1.0.5 final)
  + High: Tools: crm_resource - Advertise --move instead of --migrate
  + Medium: Extra: New node connectivity RA that uses system ping and attrd_updater
  + Medium: crmd: Note that dc-deadtime can be used to mask the brokeness of some switches

* Tue Aug 11 2009 Ville Skyttä <ville.skytta@iki.fi> - 1.0.5-0.7.c9120a53a6ae.hg
- Use bzipped upstream tarball.

* Wed Jul  29 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.6.c9120a53a6ae.hg
- Add back missing build auto* dependancies
- Minor cleanups to the install directive

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.5.c9120a53a6ae.hg
- Add a leading zero to the revision when alphatag is used

* Tue Jul  28 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.5-0.4.c9120a53a6ae.hg
- Incorporate the feedback from the cluster-glue review
- Realistically, the version is a 1.0.5 pre-release
- Use the global directive instead of define for variables
- Use the haclient/hacluster group/user instead of daemon
- Use the _configure macro
- Fix install dependancies

* Fri Jul  24 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-3
- Include an AUTHORS and license file in each package
- Change the library package name to pacemaker-libs to be more 
  Fedora compliant
- Remove execute permissions from xml related files
- Reference the new cluster-glue devel package name
- Update the tarball from upstream to version c9120a53a6ae
  + High: PE: Only prevent migration if the clone dependancy is stopping/starting on the target node
  + High: PE: Bug 2160 - Dont shuffle clones due to colocation
  + High: PE: New implementation of the resource migration (not stop/start) logic
  + Medium: Tools: crm_resource - Prevent use-of-NULL by requiring a resource name for the -A and -a options
  + Medium: PE: Prevent use-of-NULL in find_first_action()
  + Low: Build: Include licensing files

* Tue Jul 14 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-2
- Reference authors from the project AUTHORS file instead of listing in description
- Change Source0 to reference the project's Mercurial repo
- Cleaned up the summaries and descriptions
- Incorporate the results of Fedora package self-review

* Tue Jul 14 2009 Andrew Beekhof <andrew@beekhof.net> - 1.0.4-1
- Initial checkin
